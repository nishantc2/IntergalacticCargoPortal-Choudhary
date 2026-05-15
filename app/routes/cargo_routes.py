import csv
import io
import math

from flask import Blueprint, jsonify, request

from app.auth import get_claims_from_request
from app.db import get_connection

cargo_bp = Blueprint("cargo", __name__)


def _is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False
    limit = int(math.sqrt(number)) + 1
    for candidate in range(3, limit, 2):
        if number % candidate == 0:
            return False
    return True


def _parse_manifest(file_content: str) -> list[dict]:
    lines = [line for line in file_content.splitlines() if line.strip()]
    if not lines:
        return []

    delimiter = ","
    header_line = lines[0]
    if "|" in header_line:
        delimiter = "|"
    elif "\t" in header_line:
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    parsed_rows = []
    for row in reader:
        normalized = {str(k).strip().upper(): (v or "").strip() for k, v in row.items() if k}
        if normalized:
            parsed_rows.append(normalized)
    return parsed_rows


@cargo_bp.post("/api/upload")
def upload_manifest():
    claims = get_claims_from_request(request)
    if not claims:
        return jsonify({"message": "Unauthorized."}), 401
    if claims.get("role") != "Admin":
        return jsonify({"message": "Clearance level inadequate."}), 403

    upload = request.files.get("file")
    if not upload or not upload.filename:
        return jsonify({"message": "manifest.txt file is required."}), 400
    if not upload.filename.lower().endswith(".txt"):
        return jsonify({"message": "Only .txt manifest files are supported."}), 400

    content = upload.stream.read().decode("utf-8", errors="ignore")
    parsed_rows = _parse_manifest(content)
    if not parsed_rows:
        return jsonify({"message": "Manifest file is empty or invalid."}), 400

    for required in ("DESTINATION", "WEIGHT"):
        if required not in parsed_rows[0]:
            return jsonify({"message": f"Manifest must include {required} column."}), 400

    inserted = 0
    skipped_prime = 0
    skipped_invalid = 0

    with get_connection() as conn:
        for row in parsed_rows:
            destination = row.get("DESTINATION", "")
            weight_value = row.get("WEIGHT", "")

            try:
                final_weight = float(weight_value)
            except (TypeError, ValueError):
                skipped_invalid += 1
                continue

            if "Sector-7" in destination:
                final_weight *= 1.45

            rounded_weight = round(final_weight)
            if _is_prime(rounded_weight):
                skipped_prime += 1
                continue

            conn.execute(
                """
                INSERT INTO cargo_records (shipment_id, origin, destination, weight_kg)
                VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("SHIPMENT_ID") or row.get("ID"),
                    row.get("ORIGIN"),
                    destination,
                    rounded_weight,
                ),
            )
            inserted += 1
        conn.commit()

    return (
        jsonify(
            {
                "message": "Manifest processed successfully.",
                "inserted": inserted,
                "skipped_prime": skipped_prime,
                "skipped_invalid": skipped_invalid,
            }
        ),
        201,
    )


@cargo_bp.get("/api/cargo")
def get_cargo_records():
    claims = get_claims_from_request(request)
    if not claims:
        return jsonify({"message": "Unauthorized."}), 401

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, shipment_id, origin, destination, weight_kg, uploaded_at
            FROM cargo_records
            ORDER BY id DESC
            """
        ).fetchall()

    return (
        jsonify(
            {
                "cargo": [
                    {
                        "id": row["id"],
                        "shipment_id": row["shipment_id"],
                        "origin": row["origin"],
                        "destination": row["destination"],
                        "weight_kg": row["weight_kg"],
                        "uploaded_at": row["uploaded_at"],
                    }
                    for row in rows
                ]
            }
        ),
        200,
    )
