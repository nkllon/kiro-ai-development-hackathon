# Pull Request

## Description

**Summary**
Brief description of the changes made in this pull request.

**Motivation and Context**
Why is this change required? What problem does it solve?

**Type of Change**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Security improvement
- [ ] Other (please describe):

## Related Issues

**Closes Issues**
- Closes #123
- Fixes #456

**Related Issues**
- Related to #789
- Addresses #101

## Changes Made

**Detailed Changes**
- [ ] Change 1: Description
- [ ] Change 2: Description
- [ ] Change 3: Description

**Files Modified**
- `src/module1/file1.py`: Description of changes
- `docs/section/file.md`: Description of changes
- `tests/test_module.py`: Description of changes

**New Files Added**
- `src/new_module/new_file.py`: Description of purpose
- `docs/new_section/new_doc.md`: Description of content

## Security Checklist

**Credential Management**
- [ ] No hardcoded credentials in source code
- [ ] All sensitive data uses environment variables
- [ ] Proper error handling for missing credentials
- [ ] Security documentation updated if needed

**Code Security**
- [ ] Input validation implemented where needed
- [ ] No SQL injection vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] Proper error handling without information disclosure

**Dependencies**
- [ ] No new vulnerable dependencies added
- [ ] Dependency versions properly pinned
- [ ] Security scan passes

## Testing

**Test Coverage**
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] End-to-end tests added/updated
- [ ] Security tests added/updated

**Test Results**
```bash
# Paste test results here
pytest tests/ --run
================================ test session starts ================================
...
================================ X passed in Y.YYs ================================
```

**Manual Testing**
- [ ] Feature works as expected
- [ ] No regression in existing functionality
- [ ] Examples still work correctly
- [ ] Documentation examples tested

**Performance Testing**
- [ ] No significant performance regression
- [ ] Memory usage is acceptable
- [ ] Response times are acceptable

## Code Quality

**Code Standards**
- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Code is properly commented

**Code Quality Checks**
```bash
# Paste code quality check results
black --check src/ tests/
ruff check src/ tests/
mypy src/
bandit -r src/
```

**Documentation**
- [ ] Code is self-documenting
- [ ] Complex logic is explained in comments
- [ ] API documentation updated
- [ ] User documentation updated

## Documentation Updates

**Documentation Changes**
- [ ] README updated
- [ ] API documentation updated
- [ ] User guides updated
- [ ] Examples updated
- [ ] Changelog updated

**Documentation Testing**
- [ ] All code examples in documentation work
- [ ] Links are valid and working
- [ ] Documentation is clear and accurate

## Backward Compatibility

**Breaking Changes**
- [ ] No breaking changes
- [ ] Breaking changes documented
- [ ] Migration guide provided
- [ ] Deprecation warnings added

**API Changes**
- [ ] No API changes
- [ ] API changes are backward compatible
- [ ] API changes documented
- [ ] Version number updated appropriately

## Deployment Considerations

**Environment Variables**
- [ ] New environment variables documented
- [ ] Default values provided where appropriate
- [ ] Environment variable validation added

**Configuration Changes**
- [ ] Configuration changes documented
- [ ] Backward compatibility maintained
- [ ] Migration instructions provided

**Infrastructure Changes**
- [ ] No infrastructure changes required
- [ ] Infrastructure changes documented
- [ ] Deployment instructions updated

## Review Checklist

**For Reviewers**
Please verify:
- [ ] Code follows project standards and conventions
- [ ] No hardcoded credentials or sensitive data
- [ ] Tests are comprehensive and passing
- [ ] Documentation is accurate and complete
- [ ] Security considerations are addressed
- [ ] Performance impact is acceptable
- [ ] Breaking changes are properly handled

**Security Review**
- [ ] Code reviewed for security vulnerabilities
- [ ] Credential management follows best practices
- [ ] Input validation is appropriate
- [ ] Error handling doesn't leak sensitive information

## Additional Notes

**Implementation Details**
Any additional implementation details or design decisions:

**Known Issues**
Any known issues or limitations:

**Future Work**
Any follow-up work that should be done:

**Screenshots**
If applicable, add screenshots to help explain your changes:

## Checklist

**Before submitting this pull request, I confirm:**
- [ ] I have read the [Contributing Guidelines](CONTRIBUTING.md)
- [ ] I have followed the project's coding standards
- [ ] I have added tests for my changes
- [ ] All tests are passing
- [ ] I have updated documentation as needed
- [ ] I have not included any hardcoded credentials
- [ ] I have tested my changes thoroughly
- [ ] I have considered backward compatibility
- [ ] I have provided a clear description of my changes

**For maintainers:**
- [ ] Code review completed
- [ ] Security review completed
- [ ] Documentation review completed
- [ ] Tests reviewed and passing
- [ ] Ready to merge