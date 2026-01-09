# Perfect Labeler

A **multi-tenant label / receipt design backend** built using **Supabase**, **PostgreSQL**, **Row Level Security (RLS)**, and **REST APIs**.
The system allows authenticated users to create and manage label designs while ensuring **strict tenant-level data isolation**.

---

## Project Objective

The goal of this project is to build a secure backend where:

* Users authenticate using **Supabase Auth (Email & Password)**
* Each user belongs to a **tenant**
* Tenants can:

  * Create receipt / label designs
  * Add design elements (text, QR, barcode, logo, etc.)
* **No tenant can access another tenant’s data**
* Security is enforced at the **database level**
* All APIs can be tested using **Postman**

---

## Tech Stack

* **Backend & Database**: Supabase (PostgreSQL)
* **Authentication**: Supabase Auth
* **Security**: Row Level Security (RLS)
* **APIs**: Supabase Auto-generated REST APIs
* **Testing**: Postman (VS Code extension)
* **Future Client**: Flask

---

## Database Schema

### `receipt_designs`

Stores the main label / receipt layouts.

```sql
CREATE TABLE receipt_designs (
  id text PRIMARY KEY,
  tenant_id text NOT NULL,
  name text NOT NULL,
  width INT NOT NULL,
  height INT NOT NULL,
  created_at timestamptz DEFAULT NOW()
);
```

---

### `receipt_elements`

Stores individual elements inside a design.

```sql
CREATE TABLE receipt_elements (
  id text PRIMARY KEY,
  design_id text NOT NULL REFERENCES receipt_designs(id) ON DELETE CASCADE,
  tenant_id text NOT NULL,
  element_type text NOT NULL CHECK (
    element_type IN (
      'text',
      'qr',
      'line',
      'logo',
      'code128',
      'code39',
      'placeholder'
    )
  ),
  position_x INT NOT NULL,
  position_y INT NOT NULL,
  width INT NOT NULL,
  height INT NOT NULL,
  content text,
  properties JSONB,
  created_at timestamptz DEFAULT NOW()
);
```

---

## Authentication Flow

1. User signs up / logs in using **email and password**
2. Supabase returns an **access token (JWT)**
3. The JWT contains:

```json
{
  "user_metadata": {
    "tenant_id": "tenant_A"
  }
}
```

4. This JWT is sent with every API request
5. The database uses this token to decide what data the user can access

---

## Security Model (RLS Explained Simply)

* **Row Level Security (RLS)** is enabled on all tables
* Every row contains a `tenant_id`
* Every user JWT contains a `tenant_id`
* Policies enforce this rule:

```
row.tenant_id == jwt.tenant_id
```

### Example SELECT Policy

```sql
CREATE POLICY "tenant can read designs"
ON receipt_designs
FOR SELECT
USING (
  tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')
);
```

### Result:

* Correct tenant → data allowed
* Wrong tenant → data hidden or blocked
* Even the server cannot bypass this accidentally

---

## API Usage

Supabase automatically exposes REST APIs.

### Base URL

```
https://<project-id>.supabase.co/rest/v1
```

---

### Create a Design

```
POST /receipt_designs
```

Body:

```json
{
  "id": "design1",
  "tenant_id": "tenant_A",
  "name": "Invoice Label",
  "width": 400,
  "height": 600
}
```

---

### Get Designs

```
GET /receipt_designs
```

---

### Update a Design

```
PATCH /receipt_designs?id=eq.design1
```

---

### Delete a Design

```
DELETE /receipt_designs?id=eq.design1
```

---

## API Testing with Postman

### Required Headers

```
apikey: YOUR_ANON_KEY
Authorization: Bearer YOUR_USER_JWT
Content-Type: application/json
```

### Important Behavior

| Response         | Meaning               |
| ---------------- | --------------------- |
| `200 OK + []`    | RLS filtered rows     |
| `403 Forbidden`  | Policy blocked action |
| `204 No Content` | Update/Delete success |
| `404 Not Found`  | Wrong endpoint        |

➡️ An empty list does **not** mean an error
➡️ It means **security is working correctly**

---

## Edge Function Enhancement

An **Edge Function** was added to log when a new design is created.

### Purpose:

* Track design creation events
* Record tenant activity
* Enable future analytics and auditing

### Why Edge Functions:

* Runs server-side
* Secure
* Cannot be bypassed by clients
* Ideal for logging and validation

---

## Challenges Faced

* Understanding the difference between **API Key and JWT**
* Debugging empty API responses caused by RLS
* Learning that security failures can look like “success”
* Correctly linking users, JWTs, and tenant IDs
* Testing secured APIs for the first time using Postman

---

## Key Learnings

* Security should live in the **database**
* JWT is the source of user identity
* RLS prevents data leaks even if code is wrong
* Supabase REST APIs are production-ready
* Multi-tenant systems require careful planning

---

## Future Enhancements

* Flask frontend integration
* Drag-and-drop label editor
* Label rendering & printing
* Role-based permissions
* Audit dashboards per tenant

---

## Author

**Jeevanantham**
Supabase • PostgreSQL • Flask

---
Just say 👍

