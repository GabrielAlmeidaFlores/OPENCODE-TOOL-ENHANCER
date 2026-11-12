#!/usr/bin/env bash
# Name: Test pollution bisection
# Purpose: Finds the test file that creates unwanted files or state by running each test and checking for the pollution after every run.
# Usage: ./find-polluter.sh <file_or_dir_to_check> <test_pattern>
# Arguments: $1 is the path that should not exist after a test; $2 is the test glob, for example 'src/**/*.test.ts'.
# Environment: Requires bash, find, npm, and a test command at the repository root.
# Outputs: Prints progress, the offending test, and the pollution details.
# Side effects: Executes the project test suite once per matching file and may leave the pollution in place.
# References: skills/systematic-debugging/SKILL.md
set -e

# Function: list_test_files
# Description: Resolves the test glob against the working tree, accepting an optional leading ./ and collapsing **/ so files directly under the base directory also match.
# Arguments: $1 is the test pattern.
# Returns: Newline-separated matching paths.
# Side effects: None.
list_test_files() {
  local pattern="${1#./}"
  find . \( -path "./$pattern" -o -path "./${pattern//\*\*\//}" \) | sort -u
}

# Function: run_test
# Description: Runs one test file with npm and ignores its exit status because the goal is detecting side effects, not test results.
# Arguments: $1 is the test file.
# Returns: Always zero.
# Side effects: Executes the project test command.
run_test() {
  npm test "$1" > /dev/null 2>&1 || true
}

# Function: report_polluter
# Description: Prints the offending test file and the pollution details.
# Arguments: $1 is the test file, $2 is the pollution path.
# Returns: None.
# Side effects: Writes to standard output and lists the pollution path.
report_polluter() {
  echo ""
  echo "🎯 FOUND POLLUTER!"
  echo "   Test: $1"
  echo "   Created: $2"
  echo ""
  echo "Pollution details:"
  ls -la "$2"
  echo ""
  echo "To investigate:"
  echo "  npm test $1"
  echo "  cat $1"
}

# Function: main
# Description: Validates arguments, iterates over matching tests, and stops at the first polluter.
# Arguments: The script arguments.
# Returns: One when a polluter is found, zero when every test is clean.
# Side effects: Runs tests and may print progress.
main() {
  if [ $# -ne 2 ]; then
    echo "Usage: $0 <file_to_check> <test_pattern>"
    echo "Example: $0 '.git' 'src/**/*.test.ts'"
    exit 1
  fi

  local pollution_check="$1"
  local test_pattern="$2"
  local test_files
  local total
  local count=0

  test_files="$(list_test_files "$test_pattern")"

  if [ -z "$test_files" ]; then
    total=0
  else
    total=$(printf '%s\n' "$test_files" | wc -l | tr -d ' ')
  fi

  echo "🔍 Searching for test that creates: $pollution_check"
  echo "Test pattern: $test_pattern"
  echo ""
  echo "Found $total test files"
  echo ""

  for test_file in $test_files; do
    count=$((count + 1))

    if [ -e "$pollution_check" ]; then
      echo "⚠️  Pollution already exists before test $count/$total"
      echo "   Skipping: $test_file"
      continue
    fi

    echo "[$count/$total] Testing: $test_file"
    run_test "$test_file"

    if [ -e "$pollution_check" ]; then
      report_polluter "$test_file" "$pollution_check"
      exit 1
    fi
  done

  echo ""
  echo "✅ No polluter found - all tests clean!"
  exit 0
}

main "$@"
