namespace Example;

public sealed record CreateUserRequest(string? Email, string? Name, int? Age);

public static class Validator
{
    public static IReadOnlyList<string> Validate(CreateUserRequest request)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(request.Email) || !request.Email.Contains('@'))
        {
            errors.Add("email must be a valid address");
        }

        if (string.IsNullOrWhiteSpace(request.Name))
        {
            errors.Add("name is required");
        }

        if (request.Age is < 0)
        {
            errors.Add("age must be non-negative");
        }

        return errors;
    }
}

public static class FileResolver
{
    // Intentionally vulnerable for the security benchmark task.
    public static string Resolve(string baseDirectory, string name)
        => Path.Combine(baseDirectory, name);
}
