# Dockerfile Security Policy
package dockerfile.security

import rego.v1

# Deny running as root user
deny[msg] {
    input[i].Cmd == "user"
    val := input[i].Value
    contains(val[0], "root")
    msg := "Container should not run as root user"
}

# Require explicit USER instruction
deny[msg] {
    not has_user_instruction
    msg := "Dockerfile should contain explicit USER instruction (non-root)"
}

has_user_instruction {
    input[_].Cmd == "user"
}

# Deny use of latest tag
deny[msg] {
    input[i].Cmd == "from"
    val := input[i].Value[0]
    contains(val, ":latest")
    msg := "Base image should not use 'latest' tag"
}

# Require HEALTHCHECK
warn[msg] {
    not has_healthcheck
    msg := "Dockerfile should include HEALTHCHECK instruction"
}

has_healthcheck {
    input[_].Cmd == "healthcheck"
}

# Deny dangerous commands
deny[msg] {
    input[i].Cmd == "run"
    val := input[i].Value[0]
    dangerous_commands := ["curl", "wget", "sudo", "su"]
    command := dangerous_commands[_]
    contains(val, command)
    msg := sprintf("Dangerous command '%s' should be avoided or properly secured", [command])
}