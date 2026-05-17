"""Серверные интеграции с открытыми справочниками лекарств."""
from __future__ import annotations

import json
from dataclasses import dataclass
from socket import timeout as SocketTimeout
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


@dataclass(frozen=True, slots=True)
class ExternalApiRecord:
    title: str
    subtitle: str = ""
    facts: tuple[tuple[str, str], ...] = ()
    description: str = ""


@dataclass(frozen=True, slots=True)
class ExternalApiResult:
    source: str
    query: str
    status: str
    records: tuple[ExternalApiRecord, ...] = ()

    @property
    def has_records(self) -> bool:
        return bool(self.records)


class ExternalApiNoResults(Exception):
    pass


class ExternalApiError(Exception):
    pass


def _first(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    if value is None:
        return ""
    return str(value)


def _request_json(url: str, params: dict[str, str | int | None]) -> dict[str, Any]:
    clean_params = {key: value for key, value in params.items() if value not in (None, "")}
    full_url = f"{url}?{urlencode(clean_params)}" if clean_params else url
    request = Request(full_url, headers={"User-Agent": "pharmacy-project/1.0"})
    timeout = float(getattr(settings, "EXTERNAL_API_TIMEOUT", 3))

    # Keep API failures contained so views can show a simple status message.
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise ExternalApiNoResults from exc
        raise ExternalApiError(f"HTTP {exc.code}") from exc
    except (URLError, SocketTimeout, TimeoutError, json.JSONDecodeError) as exc:
        raise ExternalApiError(str(exc)) from exc


def lookup_rxnorm(query: str) -> ExternalApiResult:
    clean_query = query.strip()
    source = "RxNorm / RxNav"
    if not clean_query:
        return ExternalApiResult(source=source, query=query, status="Введите название препарата.")

    try:
        match_data = _request_json(
            "https://rxnav.nlm.nih.gov/REST/rxcui.json",
            {"name": clean_query, "search": 2},
        )
        ids = match_data.get("idGroup", {}).get("rxnormId") or []
        if not ids:
            return ExternalApiResult(source=source, query=clean_query, status="Ничего не найдено.")

        rxcui = str(ids[0])
        props_data = _request_json(f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json", {})
        props = props_data.get("properties") or {}
    except ExternalApiNoResults:
        return ExternalApiResult(source=source, query=clean_query, status="Ничего не найдено.")
    except ExternalApiError:
        return ExternalApiResult(source=source, query=clean_query, status="Справочник временно недоступен.")

    title = _first(props.get("name")) or clean_query
    facts = (
        ("RxCUI", rxcui),
        ("TTY", _first(props.get("tty")) or "—"),
        ("Язык", _first(props.get("language")) or "—"),
        ("Источник", _first(props.get("synonym")) or "RxNorm"),
    )
    record = ExternalApiRecord(title=title, subtitle="Нормализованный идентификатор лекарства", facts=facts)
    return ExternalApiResult(source=source, query=clean_query, status="Данные получены.", records=(record,))


def lookup_openfda_label(query: str) -> ExternalApiResult:
    clean_query = query.strip().replace('"', "").replace("\\", "")
    source = "openFDA Drug Label"
    if not clean_query:
        return ExternalApiResult(source=source, query=query, status="Введите название препарата.")

    api_key = getattr(settings, "OPENFDA_API_KEY", "")
    fields = ("openfda.brand_name", "openfda.generic_name", "openfda.substance_name")
    label: dict[str, Any] | None = None

    try:
        for field in fields:
            try:
                data = _request_json(
                    "https://api.fda.gov/drug/label.json",
                    {"api_key": api_key, "search": f'{field}:"{clean_query}"', "limit": 1},
                )
            except ExternalApiNoResults:
                continue
            results = data.get("results") or []
            if results:
                label = results[0]
                break
    except ExternalApiError:
        return ExternalApiResult(source=source, query=clean_query, status="Справочник временно недоступен.")

    if not label:
        return ExternalApiResult(source=source, query=clean_query, status="Ничего не найдено.")

    openfda = label.get("openfda") or {}
    title = _first(openfda.get("brand_name")) or _first(openfda.get("generic_name")) or clean_query
    facts = (
        ("МНН", _first(openfda.get("generic_name")) or "—"),
        ("Активное вещество", _first(openfda.get("substance_name")) or "—"),
        ("Производитель", _first(openfda.get("manufacturer_name")) or "—"),
        ("NDC", _first(openfda.get("product_ndc")) or "—"),
    )
    description = (
        _first(label.get("purpose"))
        or _first(label.get("indications_and_usage"))
        or _first(label.get("description"))
    )
    record = ExternalApiRecord(
        title=title,
        subtitle="Публичная маркировка FDA",
        facts=facts,
        description=description,
    )
    return ExternalApiResult(source=source, query=clean_query, status="Данные получены.", records=(record,))
