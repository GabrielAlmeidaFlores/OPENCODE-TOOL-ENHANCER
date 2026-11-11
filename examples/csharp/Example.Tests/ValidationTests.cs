using Example;
using Xunit;

namespace Example.Tests;

/// <summary>Tests for <see cref="Validator"/> and <see cref="FileResolver"/>.</summary>
public class ValidationTests
{
    /// <summary>Verifies that a valid request produces no errors.</summary>
    [Fact]
    public void AcceptsValidRequest()
    {
        var errors = Validator.Validate(new CreateUserRequest("a@b.co", "Ada", 30));
        Assert.Empty(errors);
    }

    /// <summary>Verifies that a missing email is rejected.</summary>
    [Fact]
    public void RejectsMissingEmail()
    {
        var errors = Validator.Validate(new CreateUserRequest(null, "Ada", 30));
        Assert.Contains(errors, error => error.Contains("email"));
    }

    /// <summary>Verifies that a negative age is rejected.</summary>
    [Fact]
    public void RejectsNegativeAge()
    {
        var errors = Validator.Validate(new CreateUserRequest("a@b.co", "Ada", -1));
        Assert.Contains(errors, error => error.Contains("age"));
    }

    /// <summary>Verifies that a normal file name resolves under the base directory.</summary>
    [Fact]
    public void ResolvesNormalFileName()
    {
        var result = FileResolver.Resolve("/srv/user-files", "avatar.png");
        Assert.EndsWith("/srv/user-files/avatar.png", result.Replace('\\', '/'));
    }
}
