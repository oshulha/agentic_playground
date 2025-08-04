from base import RocketChatBase


class RocketChatMiscellaneous(RocketChatBase):
    # Miscellaneous information
    def directory(self, query, **kwargs):
        """Search by users or channels on all server.
Field: text Recive type: string Description: The search term to be filtered Example: rocket
Field: type Receive type: string Description: It can be channels or users. When type is users you can send an additional workspace field, that can be local (default) or all. Workspace=all will work only if federation is enabled.
Example: users

Field: workspace
Receive type: string
Description: It can be local or all( if federation is enabled). It is local by default.
Example: local

Field: query Field is Required (will not query if not to fill it properly)
Description: The query to search the workspace directory. When type is users you can send an additional workspace field, that can be local (default) or all. Workspace=all will work only if federation is enabled.
Example: {"text": "rocket", "type": "users", "workspace": "local"}"""

        if isinstance(query, dict):
            query = str(query).replace("'", '"')

        return self.call_api_get("directory", query=query, kwargs=kwargs)