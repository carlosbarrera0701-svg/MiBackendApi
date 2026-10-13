var builder = WebApplication.CreateBuilder(args);

// Habilitar CORS para que tu app movil de Flutter pueda conectarse sin bloqueos
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

app.UseCors("AllowAll");

// Endpoint para autenticación de Login
app.MapPost("/api/auth/login", (LoginRequest request) =>
{
    if (request.Usuario == "admin" && request.Password == "1234")
    {
        return Results.Ok(new { 
            exito = true, 
            mensaje = "Bienvenido al sistema", 
            token = "token-fake-12345" 
        });
    }

    return Results.Json(new { 
        exito = false, 
        mensaje = "Usuario o contraseña incorrectos" 
    }, statusCode: 401);
});

app.Run();

record LoginRequest(string Usuario, string Password);