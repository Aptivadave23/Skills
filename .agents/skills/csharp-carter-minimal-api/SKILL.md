---
name: csharp-carter-minimal-api
description: Use this skill when the user asks for a C# ASP.NET Core minimum API or minimal API and the implementation should use Carter for endpoint organization. Trigger for requests mentioning minimum api, minimal api, Carter, Carter module, endpoint, CRUD endpoint, route, or ASP.NET Core web API work that should be implemented with Carter instead of MVC controllers. Do not use for MVC controller work, Razor Pages, SignalR, gRPC, non-.NET services, or examples that should live only in Program.cs without Carter.
---

# Mission
Create or update ASP.NET Core endpoints using Carter modules, not MVC controllers and not ad hoc Program.cs-only route mappings.

## Default architecture
- Prefer one `ICarterModule` per feature or resource.
- Keep `Program.cs` focused on startup and middleware.
- If Carter is not already wired up, add:
  - `builder.Services.AddCarter();`
  - `app.MapCarter();`
- Implement routes inside `AddRoutes(IEndpointRouteBuilder app)`.
- Put modules in the repository's existing folder convention for endpoints/modules. If no convention exists, prefer `Modules` or `Endpoints`.

## OpenAPI and Scalar Defaults
- When creating a new API project or wiring a new minimal API app, add OpenAPI and Scalar support by default, unless:
  - the repo already uses another documentation UI/pattern, or
  - the user explicitly says not to include OpenAPI or Scalar.
- Add useful endpoint metadata so generated docs are meaningful:
  - tags
  - summaries
  - descriptions
  - response metadata

## Workflow
1. Inspect the repository for existing Carter modules, endpoint patterns, folder layout, namespaces, DTO conventions, auth, validation, logging, OpenAPI usage, and test style.
2. Match the existing conventions before introducing new files or patterns.
3. When adding an endpoint, prefer:
   - Carter modules for route registration
   - handler parameter injection for services and request binding
   - `TypedResults` or the repo's existing result pattern
   - DTOs/records for non-trivial request and response payloads
   - thin handlers that delegate business logic to existing services, handlers, or application-layer code
4. Respect existing route prefixes, versioning, tags, auth policies, and error handling conventions.
5. Add only the minimum supporting code required for the endpoint to work: DTOs, service registration, validators, tests, and mappings.
6. Run the narrowest useful validation first: build the changed project, then run targeted tests if they exist.
7. If the repo already uses Swagger UI, NSwag, Redoc, or another OpenAPI approach, extend the existing pattern instead of replacing it unless the user explicitly asks for Scalar.
8. If not docs setup exists and the task is creating a new API/minimal API scaffold, wire up Scalar with a basic OpenAPI configuration and a few example tags, summaries, and descriptions to demonstrate good metadata practices.

## Guardrails
- Do not create MVC controllers unless the user explicitly asks for controllers.
- Do not put all routes in `Program.cs` unless the repository already follows that pattern and the user explicitly asks for it.
- Do not ignore existing Carter examples in the repo.
- Do not invent a new architecture when the repository already has a service or application layer.
- Do not replace an existing documentation stack just because Scalar is available.
- Do not enable documentation UIs outside development unless the user explicitly asks for it.
- Preserve existing namespaces, file naming, dependency injection patterns, and folder structure.
- For CRUD work, prefer a dedicated module such as `OrdersModule` or `WidgetsModule` over scattering related routes across unrelated files.

## Heuristics for common requests
- "create a minimum api" or "create a minimal api" means create or update a Carter module
- "add an endpoint" means use Carter unless the repo clearly uses another pattern
- "wire up a route" means route registration belongs in an `ICarterModule`
- "show me a minimal api example" means show a Carter-based example unless the user explicitly asks for raw Minimal API syntax in `Program.cs`

## Done when
- the endpoint is implemented in a Carter module
- startup wiring is present if needed
- OpenAPI/Scalar is configured when appropriate
- the change matches repository conventions
- build/tests were run when practical
- the response summarizes files changed, endpoint behavior, validation results, and assumptions