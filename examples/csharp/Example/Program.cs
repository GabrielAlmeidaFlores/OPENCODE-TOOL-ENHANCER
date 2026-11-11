namespace Example;

/// <summary>Create-user request received by the example endpoint.</summary>
/// <param name="Email">Email address supplied by the caller.</param>
/// <param name="Name">Display name supplied by the caller.</param>
/// <param name="Age">Optional age supplied by the caller.</param>
public sealed record CreateUserRequest(string? Email, string? Name, int? Age);

/// <summary>Validates create-user requests.</summary>
public static class Validator
{
    /// <summary>Validates a create-user request.</summary>
    /// <param name="request">Untrusted request data.</param>
    /// <returns>Validation errors; empty when the request is valid.</returns>
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

/// <summary>Resolves user-supplied file names under a base directory.</summary>
public static class FileResolver
{
    /// <summary>Resolves a file name under a base directory.</summary>
    /// <param name="baseDirectory">Directory containing user files.</param>
    /// <param name="name">User-supplied file name.</param>
    /// <returns>The combined path.</returns>
    /// <remarks>Intentionally vulnerable to path traversal to support the security benchmark task.</remarks>
    public static string Resolve(string baseDirectory, string name)
        => Path.Combine(baseDirectory, name);
}
