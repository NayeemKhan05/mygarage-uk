import re

from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any

from app.schemas.ai import (
    AiMotStats,
    AiRecurringItem,
    AiVehicleSnapshot,
)


AI_HISTORY_YEARS = 5


ISSUE_COMPONENTS = {
    "Brakes": (
        "brake",
        "braking",
        "brake disc",
        "brake pad",
        "parking brake",
    ),
    "Tyres and wheels": (
        "tyre",
        "tire",
        "wheel",
    ),
    "Suspension": (
        "suspension",
        "coil spring",
        "shock absorber",
        "anti-roll",
        "anti roll",
        "ball joint",
        "bush",
        "bushing",
    ),
    "Steering": (
        "steering",
        "track rod",
        "power steering",
    ),
    "Lights and electrical": (
        "lamp",
        "headlamp",
        "light",
        "indicator",
        "electrical",
    ),
    "Visibility": (
        "windscreen",
        "windshield",
        "wiper",
        "washer",
        "mirror",
    ),
    "Exhaust and emissions": (
        "exhaust",
        "emission",
        "catalytic",
        "lambda",
        "smoke",
    ),
    "Structure and corrosion": (
        "corrosion",
        "corroded",
        "structural",
        "chassis",
        "subframe",
        "sub-frame",
        "sill",
    ),
    "Driveshaft and joints": (
        "driveshaft",
        "drive shaft",
        "cv joint",
        "constant velocity",
    ),
    "Cooling system": (
        "coolant",
        "radiator",
        "cooling system",
        "water pump",
    ),
    "Leaks": (
        "oil leak",
        "fluid leak",
        "leaking",
        "leak",
    ),
    "Seat belts and restraints": (
        "seat belt",
        "seatbelt",
        "restraint",
    ),
}


def _date_text(
    value: date | datetime | None,
) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _normalise_text(
    value: str,
) -> str:
    return " ".join(
        value
        .lower()
        .strip()
        .split()
    )


def _contains_keyword(
    text: str,
    keyword: str,
) -> bool:
    pattern = (
        r"\b"
        + re.escape(keyword)
        + r"\b"
    )

    return (
        re.search(
            pattern,
            text,
        )
        is not None
    )


def _component_for_issue(
    text: str,
) -> str | None:
    normalised = (
        _normalise_text(
            text
        )
    )

    for component, keywords in ISSUE_COMPONENTS.items():
        if any(
            _contains_keyword(
                normalised,
                keyword,
            )
            for keyword in keywords
        ):
            return component

    return None


def _history_cutoff() -> date:
    today = date.today()

    try:
        return today.replace(
            year=(
                today.year
                - AI_HISTORY_YEARS
            )
        )

    except ValueError:
        return today.replace(
            year=(
                today.year
                - AI_HISTORY_YEARS
            ),
            day=28,
        )


def _within_history_window(
    completed_at: datetime | None,
) -> bool:
    if completed_at is None:
        return False

    return (
        completed_at.date()
        >= _history_cutoff()
    )


def _safe_value(
    value: Any,
) -> Any:
    if isinstance(
        value,
        (
            date,
            datetime,
        ),
    ):
        return value.isoformat()

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if value is None:
        return None

    return str(value)


def _sanitise_manual_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    excluded_fields = {
        "id",
        "user_id",
        "vehicle_id",
        "created_at",
        "updated_at",
        "stored_filename",
        "file_path",
        "receipt_path",
        "receipts",
    }

    cleaned: dict[str, Any] = {}

    for key, value in record.items():
        if key in excluded_fields:
            continue

        if value is None:
            continue

        cleaned[key] = (
            _safe_value(
                value
            )
        )

    return cleaned


def _mot_sort_key(
    completed_at: datetime | None,
) -> str:
    if completed_at is None:
        return ""

    return completed_at.isoformat()


def _serialise_defect(
    defect: Any,
) -> dict[str, Any]:
    return {
        "type": (
            defect.type
            or "UNKNOWN"
        ).upper(),

        "text": defect.text,

        "dangerous": (
            defect.dangerous
        ),
    }


def build_vehicle_context(
    vehicle: AiVehicleSnapshot,
) -> dict[str, Any]:
    all_tests = sorted(
        vehicle.mot_tests,
        key=lambda test: (
            _mot_sort_key(
                test.completed_at
            )
        ),
        reverse=True,
    )

    recent_tests = [
        test
        for test in all_tests
        if _within_history_window(
            test.completed_at
        )
    ]

    if (
        not recent_tests
        and all_tests
    ):
        recent_tests = (
            all_tests[:1]
        )

    passed = 0
    failed = 0
    recorded_items = 0

    defect_type_counts: Counter[str] = (
        Counter()
    )

    component_test_ids: dict[
        str,
        set[str],
    ] = defaultdict(set)

    component_latest: dict[
        str,
        str | None,
    ] = {}

    exact_test_ids: dict[
        str,
        set[str],
    ] = defaultdict(set)

    exact_labels: dict[
        str,
        str,
    ] = {}

    exact_latest: dict[
        str,
        str | None,
    ] = {}

    mileage_points: list[
        dict[str, Any]
    ] = []

    mot_history: list[
        dict[str, Any]
    ] = []

    for index, test in enumerate(
        recent_tests
    ):
        result = (
            test.test_result
            or "UNKNOWN"
        ).upper()

        if result == "PASSED":
            passed += 1

        elif result == "FAILED":
            failed += 1

        completed_at = (
            _date_text(
                test.completed_at
            )
        )

        test_identifier = (
            completed_at
            or f"unknown-{index}"
        )

        components_seen: set[str] = (
            set()
        )

        descriptions_seen: set[str] = (
            set()
        )

        full_recorded_items = [
            _serialise_defect(
                defect
            )
            for defect
            in test.defects
        ]

        for defect in test.defects:
            recorded_items += 1

            defect_type = (
                defect.type
                or "UNKNOWN"
            ).upper()

            defect_type_counts[
                defect_type
            ] += 1

            component = (
                _component_for_issue(
                    defect.text
                )
            )

            if (
                component
                and component
                not in components_seen
            ):
                component_test_ids[
                    component
                ].add(
                    test_identifier
                )

                components_seen.add(
                    component
                )

                previous_date = (
                    component_latest.get(
                        component
                    )
                )

                if (
                    completed_at
                    and (
                        previous_date is None
                        or completed_at
                        > previous_date
                    )
                ):
                    component_latest[
                        component
                    ] = completed_at

            normalised = (
                _normalise_text(
                    defect.text
                )
            )

            if (
                normalised
                not in descriptions_seen
            ):
                exact_test_ids[
                    normalised
                ].add(
                    test_identifier
                )

                descriptions_seen.add(
                    normalised
                )

                exact_labels.setdefault(
                    normalised,
                    defect.text,
                )

                previous_date = (
                    exact_latest.get(
                        normalised
                    )
                )

                if (
                    completed_at
                    and (
                        previous_date is None
                        or completed_at
                        > previous_date
                    )
                ):
                    exact_latest[
                        normalised
                    ] = completed_at

        if (
            test.odometer_value
            is not None
        ):
            mileage_points.append(
                {
                    "date":
                        completed_at,

                    "value":
                        test.odometer_value,

                    "unit":
                        test.odometer_unit,
                }
            )

        mot_history.append(
            {
                "date":
                    completed_at,

                "result":
                    result,

                "expiry_date":
                    _date_text(
                        test.expiry_date
                    ),

                "mileage":
                    test.odometer_value,

                "mileage_unit":
                    test.odometer_unit,

                "recorded_item_count":
                    len(
                        full_recorded_items
                    ),

                "recorded_items":
                    full_recorded_items,
            }
        )

    recurring_components = [
        {
            "label":
                component,

            "test_count":
                len(
                    test_ids
                ),

            "latest_date":
                component_latest.get(
                    component
                ),
        }
        for component, test_ids
        in component_test_ids.items()
        if len(test_ids) >= 2
    ]

    recurring_components.sort(
        key=lambda item: (
            -item[
                "test_count"
            ],
            item[
                "label"
            ],
        )
    )

    repeated_exact_items = [
        {
            "description":
                exact_labels[
                    description
                ],

            "test_count":
                len(
                    test_ids
                ),

            "latest_date":
                exact_latest.get(
                    description
                ),
        }
        for description, test_ids
        in exact_test_ids.items()
        if len(test_ids) >= 2
    ]

    repeated_exact_items.sort(
        key=lambda item: (
            -item[
                "test_count"
            ],
            item[
                "description"
            ],
        )
    )

    mileage_points.sort(
        key=lambda point: (
            point[
                "date"
            ]
            or ""
        )
    )

    mileage_decreases = 0

    for index in range(
        1,
        len(
            mileage_points
        ),
    ):
        previous = (
            mileage_points[
                index - 1
            ]
        )

        current = (
            mileage_points[
                index
            ]
        )

        previous_unit = (
            previous[
                "unit"
            ]
            or ""
        ).lower()

        current_unit = (
            current[
                "unit"
            ]
            or ""
        ).lower()

        if (
            previous_unit
            == current_unit
            and current[
                "value"
            ]
            < previous[
                "value"
            ]
        ):
            mileage_decreases += 1

    first_mileage = (
        mileage_points[0]
        if mileage_points
        else None
    )

    latest_mileage = (
        mileage_points[-1]
        if mileage_points
        else None
    )

    annual_distance: dict[
        str,
        Any,
    ] | None = None

    if (
        first_mileage
        and latest_mileage
        and first_mileage["date"]
        and latest_mileage["date"]
    ):
        first_unit = (
            first_mileage[
                "unit"
            ]
            or ""
        ).lower()

        latest_unit = (
            latest_mileage[
                "unit"
            ]
            or ""
        ).lower()

        if (
            first_unit
            and first_unit
            == latest_unit
            and latest_mileage[
                "value"
            ]
            >= first_mileage[
                "value"
            ]
        ):
            try:
                first_date = (
                    datetime.fromisoformat(
                        first_mileage[
                            "date"
                        ]
                    )
                )

                latest_date = (
                    datetime.fromisoformat(
                        latest_mileage[
                            "date"
                        ]
                    )
                )

                days = (
                    latest_date
                    - first_date
                ).days

                if days >= 180:
                    distance = (
                        latest_mileage[
                            "value"
                        ]
                        - first_mileage[
                            "value"
                        ]
                    )

                    annual_distance = {
                        "estimate":
                            round(
                                distance
                                / days
                                * 365
                            ),

                        "unit":
                            first_mileage[
                                "unit"
                            ],
                    }

            except (
                TypeError,
                ValueError,
            ):
                annual_distance = None

    service_records = [
        _sanitise_manual_record(
            record
        )
        for record
        in (
            vehicle
            .supplementary_service_records[
                :5
            ]
        )
    ]

    service_records = [
        record
        for record in service_records
        if record
    ]

    maintenance_items = [
        _sanitise_manual_record(
            record
        )
        for record
        in (
            vehicle
            .supplementary_maintenance_items[
                :5
            ]
        )
    ]

    maintenance_items = [
        record
        for record in maintenance_items
        if record
    ]

    context: dict[str, Any] = {
        "analysis_date":
            date.today()
            .isoformat(),

        "analysis_scope": {
            "years":
                AI_HISTORY_YEARS,

            "cutoff_date":
                _history_cutoff()
                .isoformat(),

            "total_mot_tests_available":
                len(
                    all_tests
                ),

            "mot_tests_analysed":
                len(
                    recent_tests
                ),
        },

        "vehicle": {
            "registration":
                vehicle.registration,

            "make":
                vehicle.make,

            "model":
                vehicle.model,

            "fuel_type":
                vehicle.fuel_type,

            "engine_size":
                vehicle.engine_size,

            "colour":
                vehicle.colour,

            "year":
                vehicle.year,
        },

        "mot_analysis": {
            "statistics": {
                "tests":
                    len(
                        recent_tests
                    ),

                "passed":
                    passed,

                "failed":
                    failed,

                "recorded_items":
                    recorded_items,

                "dangerous":
                    defect_type_counts[
                        "DANGEROUS"
                    ],

                "major":
                    defect_type_counts[
                        "MAJOR"
                    ],

                "minor":
                    defect_type_counts[
                        "MINOR"
                    ],

                "advisory":
                    defect_type_counts[
                        "ADVISORY"
                    ],

                "prs":
                    defect_type_counts[
                        "PRS"
                    ],

                "mileage_points":
                    len(
                        mileage_points
                    ),

                "mileage_decreases":
                    mileage_decreases,
            },

            "recurring_components":
                recurring_components[
                    :8
                ],

            "repeated_exact_items":
                repeated_exact_items[
                    :8
                ],

            "mileage": {
                "first_reading":
                    first_mileage,

                "latest_reading":
                    latest_mileage,

                "annual_distance_estimate":
                    annual_distance,

                "recorded_decreases":
                    mileage_decreases,

                "points":
                    mileage_points,
            },

            "mot_history":
                mot_history,
        },
    }

    if (
        service_records
        or maintenance_items
    ):
        context[
            "supplementary_user_records"
        ] = {
            "warning": (
                "These records were entered "
                "manually by the user and may "
                "be partial or incomplete. "
                "They are supplementary only."
            ),

            "service_records":
                service_records,

            "maintenance_items":
                maintenance_items,
        }

    return context


def build_mot_stats(
    context: dict[str, Any],
) -> AiMotStats:
    statistics = (
        context[
            "mot_analysis"
        ][
            "statistics"
        ]
    )

    return AiMotStats(
        **statistics
    )


def build_recurring_items(
    context: dict[str, Any],
) -> list[AiRecurringItem]:
    recurring = (
        context[
            "mot_analysis"
        ][
            "recurring_components"
        ]
    )

    return [
        AiRecurringItem(
            label=(
                item[
                    "label"
                ]
            ),

            count=(
                item[
                    "test_count"
                ]
            ),

            latest_date=(
                item[
                    "latest_date"
                ]
            ),
        )
        for item
        in recurring[:6]
    ]