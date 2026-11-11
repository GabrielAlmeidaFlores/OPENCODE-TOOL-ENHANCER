using Example;
using Xunit;

namespace Example.Tests;

public class ValidationTests
{
    [Fact]
    public void AcceptsValidRequest()
    {
        var errors = Validator.Validate(new CreateUserRequest("a@b.co", "Ada", 30));
        Assert.Empty(errors);
    }

    [Fact]
    public void RejectsMissingEmail()
    {
        var errors = Validator.Validate(new CreateUserRequest(null, "Ada", 30));
        Assert.Contains(errors, e => e.Contains("email"));
    }

    [Fact]
    public void RejectsNegativeAge()
    {
        var errors = Validator.Validate(new CreateUserRequest("a@b.co", "Ada", -1));
        Assert.Contains(errors, e => e.Contains("age"));
    }

    [Fact]
    public void ResolvesNormalFileName()
    {
        var result = FileResolver.Resolve("/srv/user-files", "avatar.png");
        Assert.EndsWith("/srv/user-files/avatar.png", result.Replace('\\', '/'));
    }
}
