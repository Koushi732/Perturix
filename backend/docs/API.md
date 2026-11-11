# Perturix REST API Documentation

All API responses are wrapped in the `StandardResponse` model.
```json
{
  "success": true,
  "message": "Success message",
  "data": { ... },
  "metadata": { "request_id": "..." },
  "timestamp": "2026-07-26T00:00:00Z",
  "request_id": "..."
}
```

## `/api/v1/images/upload`
**POST**
Uploads an image, creates a ProcessingSession, and returns metadata.
- **Request**: `multipart/form-data` with key `image`.
- **Response**: `data` contains ProcessingSession UUID and image metadata.

## `/api/v1/images/{filename}`
**GET**
Serves the raw image file for the frontend to render natively.

## `/api/v1/attacks/execute`
**POST**
Executes an adversarial attack via the AI Engine.
- **Request Body**:
```json
{
  "session_id": "uuid-string",
  "attack_name": "fgsm",
  "parameters": { "epsilon": 0.05 }
}
```
- **Response**: Returns metrics about the executed attack.

## `/api/v1/attacks/{session_id}`
**GET**
Retrieves all attacks associated with a session.

## `/api/v1/evaluation/execute`
**POST**
Runs the Evaluation Engine on a protected session.
- **Request Body**: `{ "session_id": "uuid-string" }`
- **Response**: Returns comprehensive robustness and fidelity metrics (SSIM, PSNR, LPIPS, Confidence Drop).

## `/api/v1/evaluation/{session_id}`
**GET**
Retrieves previously computed evaluation metrics.

## `/api/v1/history/`
**GET**
Lists paginated processing history.
- **Query Params**: `skip`, `limit`, `status`, `image_hash`

## `/api/v1/history/{session_id}`
**DELETE**
Cascading deletion of a session and its attack/evaluation records.
