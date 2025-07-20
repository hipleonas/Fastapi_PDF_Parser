"""
=====This file is used to practice FastAPI =====
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
"""


#YOU CANNOT REDEFINE THE SAME PATH LIKE /users and /users again





"""
========================================================FASTAPI CLI========================================================

fastapi dev initiates development mode
By defautl, auto-reload is enabled, which means the server will automatically restart when code changes are detected.
Executing fastapi run starts FastAPI in production mode by default.

There are several ways to do it depending on your specific use case and the tools that you use.

You could deploy a server yourself using a combination of tools, you could use a cloud service that does part of the work for you, or other possible options.

I will show you some of the main concepts you should probably keep in mind when deploying a FastAPI application (although most of it applies to any other type of web application).

Order matters¶
When creating path operations, you can find situations where you have a fixed path.

Like /users/me, let's say that it's to get data about the current user.

And then you can also have a path /users/{user_id} to get data about a specific user by some user ID.

Because path operations are evaluated in order, you need to make sure that the path for /users/me is declared before the one for /users/{user_id}:
"""




