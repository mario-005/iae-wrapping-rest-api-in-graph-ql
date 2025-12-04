import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from ariadne import QueryType, ObjectType, make_executable_schema
from ariadne.asgi import GraphQL

# --- 1. MOCK DATABASE (Anggap ini Database Lama) ---
users_db = [
    {"id": 1, "username": "budi_santoso", "email": "budi@example.com"},
    {"id": 2, "username": "siti_aminah", "email": "siti@example.com"},
]

posts_db = [
    {"id": 101, "user_id": 1, "title": "Belajar IAE", "content": "FastAPI itu sangat cepat..."},
    {"id": 102, "user_id": 1, "title": "GraphQL vs REST", "content": "Keduanya punya kelebihan..."},
    {"id": 103, "user_id": 2, "title": "Tutorial Ariadne", "content": "Schema-first itu asik..."},
]

# --- 2. REST API DEFINITION ---
app = FastAPI(title="REST to GraphQL Wrapper")

@app.get("/rest/users", tags=["REST"])
async def get_all_users():
    return users_db

@app.get("/rest/users/{user_id}", tags=["REST"])
async def get_user(user_id: int):
    # Mencari user berdasarkan ID
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/rest/users/{user_id}/posts", tags=["REST"])
async def get_posts_by_user(user_id: int):
    # Filter postingan berdasarkan user_id
    return [p for p in posts_db if p["user_id"] == user_id]

# --- 3. GRAPHQL SCHEMA ---
# Perhatikan: Kita menambahkan field 'posts' di dalam User,
# padahal di endpoint /rest/users data itu tidak ada.
# Kita akan menggabungkannya nanti di Resolver.
type_defs = """
    type Query {
        users: [User]
        user(id: ID!): User
    }

    type User {
        id: ID!
        username: String!
        email: String!
        posts: [Post] 
    }

    type Post {
        id: ID!
        title: String!
        content: String!
    }
"""

# --- 4. RESOLVERS (Jembatan GraphQL ke REST) ---

query = QueryType()
user_type = ObjectType("User")

# URL dasar REST API kita (localhost)
REST_API_URL = "http://127.0.0.1:8000/rest"

# Resolver untuk Query: users (Ambil semua user)
@query.field("users")
async def resolve_users(*_):
    async with httpx.AsyncClient() as client:
        # Panggil REST API
        response = await client.get(f"{REST_API_URL}/users")
        response.raise_for_status()
        return response.json()

# Resolver untuk Query: user (Ambil satu user by ID)
@query.field("user")
async def resolve_user(*_, id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{REST_API_URL}/users/{id}")
        if response.status_code == 404:
            return None
        return response.json()

# Resolver KHUSUS untuk field 'posts' milik User
# Ini yang disebut "Data Stitching" atau penggabungan data.
@user_type.field("posts")
async def resolve_user_posts(user_obj, info):
    # user_obj adalah data user yang didapat dari resolver sebelumnya
    user_id = user_obj.get("id")
    
    async with httpx.AsyncClient() as client:
        # Panggil endpoint REST yang berbeda untuk ambil postingan
        response = await client.get(f"{REST_API_URL}/users/{user_id}/posts")
        return response.json()

# --- 5. SETUP APP ---
schema = make_executable_schema(type_defs, query, user_type)
graphql_app = GraphQL(schema, debug=True)

# Pasang aplikasi GraphQL di route /graphql
app.add_route("/graphql", graphql_app)

if __name__ == "__main__":
    # Jalankan server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
