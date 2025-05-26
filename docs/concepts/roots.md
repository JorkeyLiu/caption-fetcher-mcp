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

Concepts

Roots

[User Guide](/introduction)[SDKs](/sdk/java/mcp-
overview)[Specification](/specification/2025-03-26)

[User Guide](/introduction)[SDKs](/sdk/java/mcp-
overview)[Specification](/specification/2025-03-26)

* [GitHub](https://github.com/modelcontextprotocol)

Roots are a concept in MCP that define the boundaries where servers can
operate. They provide a way for clients to inform servers about relevant
resources and their locations.

##

​

What are Roots?

A root is a URI that a client suggests a server should focus on. When a client
connects to a server, it declares which roots the server should work with.
While primarily used for filesystem paths, roots can be any valid URI
including HTTP URLs.

For example, roots could be:

    
    
    file:///home/user/projects/myapp
    https://api.example.com/v1
    

##

​

Why Use Roots?

Roots serve several important purposes:

  1. **Guidance** : They inform servers about relevant resources and locations
  2. **Clarity** : Roots make it clear which resources are part of your workspace
  3. **Organization** : Multiple roots let you work with different resources simultaneously

##

​

How Roots Work

When a client supports roots, it:

  1. Declares the `roots` capability during connection
  2. Provides a list of suggested roots to the server
  3. Notifies the server when roots change (if supported)

While roots are informational and not strictly enforcing, servers should:

  1. Respect the provided roots
  2. Use root URIs to locate and access resources
  3. Prioritize operations within root boundaries

##

​

Common Use Cases

Roots are commonly used to define:

  * Project directories
  * Repository locations
  * API endpoints
  * Configuration locations
  * Resource boundaries

##

​

Best Practices

When working with roots:

  1. Only suggest necessary resources
  2. Use clear, descriptive names for roots
  3. Monitor root accessibility
  4. Handle root changes gracefully

##

​

Example

Here’s how a typical MCP client might expose roots:

    
    
    {
      "roots": [
        {
          "uri": "file:///home/user/projects/frontend",
          "name": "Frontend Repository"
        },
        {
          "uri": "https://api.example.com/v1",
          "name": "API Endpoint"
        }
      ]
    }
    

This configuration suggests the server focus on both a local repository and an
API endpoint while keeping them logically separated.

Was this page helpful?

YesNo

[Sampling](/docs/concepts/sampling)[Transports](/docs/concepts/transports)

On this page

  * What are Roots?
  * Why Use Roots?
  * How Roots Work
  * Common Use Cases
  * Best Practices
  * Example

