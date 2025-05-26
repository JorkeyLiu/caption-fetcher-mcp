[Model Context Protocol home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/dark.svg)](/)

Search...

* [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
* [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
* [Java SDK](https://github.com/modelcontextprotocol/java-sdk)
* [Kotlin SDK](https://github.com/modelcontextprotocol/kotlin-sdk)
* [C# SDK](https://github.com/modelcontextprotocol/csharp-sdk)
* [Swift SDK](https://github.com/modelcontextprotocol/swift-sdk)

##### Get Started

  * [Introduction](/introduction)
  * Quickstart

  * [Example Servers](/examples)
  * [Example Clients](/clients)
  * [FAQs](/faqs)

##### Tutorials

  * [Building MCP with LLMs](/tutorials/building-mcp-with-llms)
  * [Debugging](/docs/tools/debugging)
  * [Inspector](/docs/tools/inspector)

##### Concepts

  * [Core architecture](/docs/concepts/architecture)
  * [Resources](/docs/concepts/resources)
  * [Prompts](/docs/concepts/prompts)
  * [Tools](/docs/concepts/tools)
  * [Sampling](/docs/concepts/sampling)
  * [Roots](/docs/concepts/roots)
  * [Transports](/docs/concepts/transports)

##### Development

  * [What's New](/development/updates)
  * [Roadmap](/development/roadmap)
  * [Contributing](/development/contributing)

[Model Context Protocol home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/mcp/logo/dark.svg)](/)

Search...

Search...

Navigation

Tutorials

Inspector

[User Guide](/introduction)[SDKs](/sdk/java/mcp-
overview)[Specification](/specification/2025-03-26)

[User Guide](/introduction)[SDKs](/sdk/java/mcp-
overview)[Specification](/specification/2025-03-26)

* [GitHub](https://github.com/modelcontextprotocol)

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is an
interactive developer tool for testing and debugging MCP servers. While the
[Debugging Guide](/docs/tools/debugging) covers the Inspector as part of the
overall debugging toolkit, this document provides a detailed exploration of
the Inspector’s features and capabilities.

##

​

Getting started

###

​

Installation and basic usage

The Inspector runs directly through `npx` without requiring installation:

    
    
    npx @modelcontextprotocol/inspector <command>
    
    
    
    npx @modelcontextprotocol/inspector <command> <arg1> <arg2>
    

####

​

Inspecting servers from NPM or PyPi

A common way to start server packages from [NPM](https://npmjs.com) or
[PyPi](https://pypi.com).

  * NPM package
  * PyPi package

    
    
    npx -y @modelcontextprotocol/inspector npx <package-name> <args>
    # For example
    npx -y @modelcontextprotocol/inspector npx server-postgres postgres://127.0.0.1/testdb
    
    
    
    npx -y @modelcontextprotocol/inspector npx <package-name> <args>
    # For example
    npx -y @modelcontextprotocol/inspector npx server-postgres postgres://127.0.0.1/testdb
    
    
    
    npx @modelcontextprotocol/inspector uvx <package-name> <args>
    # For example
    npx @modelcontextprotocol/inspector uvx mcp-server-git --repository ~/code/mcp/servers.git
    

####

​

Inspecting locally developed servers

To inspect servers locally developed or downloaded as a repository, the most
common way is:

  * TypeScript
  * Python

    
    
    npx @modelcontextprotocol/inspector node path/to/server/index.js args...
    
    
    
    npx @modelcontextprotocol/inspector node path/to/server/index.js args...
    
    
    
    npx @modelcontextprotocol/inspector \
      uv \
      --directory path/to/server \
      run \
      package-name \
      args...
    

Please carefully read any attached README for the most accurate instructions.

##

​

Feature overview

The MCP Inspector interface

The Inspector provides several features for interacting with your MCP server:

###

​

Server connection pane

  * Allows selecting the [transport](/docs/concepts/transports) for connecting to the server
  * For local servers, supports customizing the command-line arguments and environment

###

​

Resources tab

  * Lists all available resources
  * Shows resource metadata (MIME types, descriptions)
  * Allows resource content inspection
  * Supports subscription testing

###

​

Prompts tab

  * Displays available prompt templates
  * Shows prompt arguments and descriptions
  * Enables prompt testing with custom arguments
  * Previews generated messages

###

​

Tools tab

  * Lists available tools
  * Shows tool schemas and descriptions
  * Enables tool testing with custom inputs
  * Displays tool execution results

###

​

Notifications pane

  * Presents all logs recorded from the server
  * Shows notifications received from the server

##

​

Best practices

###

​

Development workflow

  1. Start Development

     * Launch Inspector with your server
     * Verify basic connectivity
     * Check capability negotiation
  2. Iterative testing

     * Make server changes
     * Rebuild the server
     * Reconnect the Inspector
     * Test affected features
     * Monitor messages
  3. Test edge cases

     * Invalid inputs
     * Missing prompt arguments
     * Concurrent operations
     * Verify error handling and error responses

##

​

Next steps

## [Inspector RepositoryCheck out the MCP Inspector source
code](https://github.com/modelcontextprotocol/inspector)## [Debugging
GuideLearn about broader debugging strategies](/docs/tools/debugging)

Was this page helpful?

YesNo

[Debugging](/docs/tools/debugging)[Core
architecture](/docs/concepts/architecture)

On this page

  * Getting started
  * Installation and basic usage
  * Inspecting servers from NPM or PyPi
  * Inspecting locally developed servers
  * Feature overview
  * Server connection pane
  * Resources tab
  * Prompts tab
  * Tools tab
  * Notifications pane
  * Best practices
  * Development workflow
  * Next steps

