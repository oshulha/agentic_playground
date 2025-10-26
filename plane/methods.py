from typing import Any, Dict, List, Optional

from base import PlaneBase
from schemas import (
    Cycle,
    CycleCreate,
    Issue,
    IssueCreate,
    Label,
    LabelCreate,
    Module,
    ModuleCreate,
    State,
    StateCreate,
)


class Plane(PlaneBase):
    def __get_project_id_by_identifier(self, identifier: str) -> Optional[str]:
        all_projects = self.list_projects()
        for project in all_projects:
            if project.get("identifier") == identifier:
                return project.get("id")
        return None

    # Project methods
    def create_project(
        self, name: str, identifier: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project.

        Args:
            name (str): The name of the project.
            identifier (str): The unique identifier for the project.
            description (str, optional): A brief description of the project. Defaults to None.

        Returns:
            Dict[str, Any]: The details of the created project.
        """
        body = {"name": name, "identifier": identifier}
        if description:
            body["description"] = description
        return self.call_api_post("projects/", body).json()

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects from the current user.

        Returns:
            List[Dict[str, Any]]: A list of projects with their shortened details.
        """
        result = self.call_api_get("projects/").json()
        projects = map(
            lambda project: {
                "name": project.get("name"),
                "id": project.get("id"),
                "identifier": project.get("identifier"),
                "description": project.get("description"),
                "project_lead": project.get("project_lead"),
            },
            result.get("results", []),
        )
        return list(projects)

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get details of a specific project.

        Args:
            project_id (str): The ID of the project to retrieve. Can be both ID or readable identifier. Preferably ID.

        Returns:
            Dict[str, Any]: A dictionary containing the project details.
        """
        result = self.call_api_get(f"projects/{project_id}/")
        if not result.ok:
            id_ = self.__get_project_id_by_identifier(project_id)
            if id_:
                result = self.call_api_get(f"projects/{id_}/")
        return result.json()

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update project details.

        Args:
            project_id (str): The ID of the project to update.
            name (str, optional): The new name for the project. Defaults to None.
            description (str, optional): The new description for the project. Defaults to None.

        Returns:
            Dict[str, Any]: The updated project details.
        """
        body = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description
        return self.call_api_patch(f"projects/{project_id}/", body).json()

    # MOVED TO FRONTEND METHODS
    # def delete_project(self, project_id: str) -> Dict[str, str]:
    #     """Delete a project.

    #     Args:
    #         project_id (str): The ID of the project to delete. Can be both ID or readable identifier. Preferably ID.

    #     Returns:
    #         Dict[str, str]: feedback message about the deletion status.
    #     """
    #     result = self.call_api_delete(f"projects/{project_id}/")
    #     if not result.ok:
    #         id_ = self.__get_project_id_by_identifier(project_id)
    #         if id_:
    #             result = self.call_api_delete(f"projects/{id_}/")
    #     if result.ok:
    #         return {"message": "Project deleted successfully."}
    #     return result.json()

    # Issue methods
    def create_issue(self, project_id: str, issue_data: IssueCreate) -> Dict[str, Any]:
        """Create an issue in a specific project.

        Args:
            project_id (str): The ID of the project to add the issue to.
            issue_data (IssueCreate): The data for the issue to be created.

        Returns:
            Dict[str, Any]: The created issue details.
        """
        if isinstance(issue_data, dict):
            issue_data = IssueCreate(**issue_data)
        return self.call_api_post(
            f"projects/{project_id}/issues/",
            issue_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def list_issues(self, project_id: str) -> List[Dict[str, Any]]:
        """List all issues in a project.

        Args:
            project_id (str): The ID of the project to list issues for.

        Returns:
            List[Dict[str, Any]]: A list of issues in the project.
        """
        result = self.call_api_get(f"projects/{project_id}/issues/").json()
        return result.get("results", [])

    def get_issue(self, project_id: str, issue_id: str) -> Dict[str, Any]:
        """Get an issue by its ID.

        Args:
            project_id (str): The ID of the project the issue belongs to.
            issue_id (str): The ID of the issue to retrieve.

        Returns:
            Dict[str, Any]: The details of the issue.
        """
        return self.call_api_get(f"projects/{project_id}/issues/{issue_id}/").json()

    def update_issue(
        self, project_id: str, issue_id: str, issue_data: Issue
    ) -> Dict[str, Any]:
        """Update issue details.

        Args:
            project_id (str): The ID of the project the issue belongs to.
            issue_id (str): The ID of the issue to update.
            issue_data (Issue): The updated issue data.

        Returns:
            Dict[str, Any]: The details of the updated issue.
        """
        if isinstance(issue_data, dict):
            issue_data = Issue(**issue_data)
        return self.call_api_patch(
            f"projects/{project_id}/issues/{issue_id}/",
            issue_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def delete_issue(self, project_id: str, issue_id: str) -> Dict[str, Any]:
        """Delete an issue.

        Args:
            project_id (str): The ID of the project the issue belongs to.
            issue_id (str): The ID of the issue to delete.

        Returns:
            Dict[str, Any]: A message indicating the result of the deletion.
        """
        result = self.call_api_delete(f"projects/{project_id}/issues/{issue_id}/")
        if result.ok:
            return {"message": "Issue deleted successfully."}
        return result.json()

    # Issue metadata methods
    # State
    def create_state(self, project_id: str, state_data: StateCreate) -> Dict[str, Any]:
        """Create a new state.

        Args:
            project_id (str): The ID of the project to create the state in.
            state_data (StateCreate): The data for the new state.

        Returns:
            Dict[str, Any]: The details of the created state.
        """
        if isinstance(state_data, dict):
            state_data = StateCreate(**state_data)
        return self.call_api_post(
            f"projects/{project_id}/states/",
            state_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def list_states(self, project_id: str) -> List[Dict[str, Any]]:
        """List all states in a project.

        Args:
            project_id (str): The ID of the project to list states for.

        Returns:
            List[Dict[str, Any]]: A list of states in the project.
        """
        result = self.call_api_get(f"projects/{project_id}/states/").json()
        return result.get("results", [])

    def get_state(self, project_id: str, state_id: str) -> Dict[str, Any]:
        """Get details of a specific state.

        Args:
            project_id (str): The ID of the project the state belongs to.
            state_id (str): The ID of the state to retrieve.

        Returns:
            Dict[str, Any]: The details of the state.
        """
        return self.call_api_get(f"projects/{project_id}/states/{state_id}/").json()

    def update_state(
        self, project_id: str, state_id: str, state_data: State
    ) -> Dict[str, Any]:
        """Update an existing state.

        Args:
            project_id (str): The ID of the project the state belongs to.
            state_id (str): The ID of the state to update.
            state_data (State): The updated state data.

        Returns:
            Dict[str, Any]: The details of the updated state.
        """
        if isinstance(state_data, dict):
            state_data = State(**state_data)
        return self.call_api_patch(
            f"projects/{project_id}/states/{state_id}/",
            state_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def delete_state(self, project_id: str, state_id: str) -> Dict[str, Any]:
        """Delete a state.

        Args:
            project_id (str): The ID of the project the state belongs to.
            state_id (str): The ID of the state to delete.

        Returns:
            Dict[str, Any]: A message indicating the result of the deletion.
        """
        result = self.call_api_delete(f"projects/{project_id}/states/{state_id}/")
        if result.ok:
            return {"message": "State deleted successfully."}
        return result.json()

    # Label
    def create_label(self, project_id: str, label_data: LabelCreate) -> Dict[str, Any]:
        """Create a new label.

        Args:
            project_id (str): The ID of the project to create the label in.
            label_data (LabelCreate): The data for the new label.

        Returns:
            Dict[str, Any]: The details of the created label.
        """
        if isinstance(label_data, dict):
            label_data = LabelCreate(**label_data)
        return self.call_api_post(
            f"projects/{project_id}/labels/",
            label_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def list_labels(self, project_id: str) -> List[Dict[str, Any]]:
        """List all labels in a project.

        Args:
            project_id (str): The ID of the project to list labels for.

        Returns:
            List[Dict[str, Any]]: A list of labels in the project.
        """
        result = self.call_api_get(f"projects/{project_id}/labels/").json()
        return result.get("results", [])

    def get_label(self, project_id: str, label_id: str) -> Dict[str, Any]:
        """Get details of a specific label.

        Args:
            project_id (str): The ID of the project the label belongs to.
            label_id (str): The ID of the label to retrieve.

        Returns:
            Dict[str, Any]: The details of the label.
        """
        return self.call_api_get(f"projects/{project_id}/labels/{label_id}/").json()

    # TODO: doesn't work, needs investigation "Label with the same external id and external source already exists"
    def update_label(
        self, project_id: str, label_id: str, label_data: Label
    ) -> Dict[str, Any]:
        """Update an existing label.

        Args:
            project_id (str): The ID of the project the label belongs to.
            label_id (str): The ID of the label to update.
            label_data (LabelCreate): The updated label data.

        Returns:
            Dict[str, Any]: The details of the updated label.
        """
        if isinstance(label_data, dict):
            label_data = Label(**label_data)
        return self.call_api_patch(
            f"projects/{project_id}/labels/{label_id}/",
            label_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def delete_label(self, project_id: str, label_id: str) -> Dict[str, Any]:
        """Delete a label.

        Args:
            project_id (str): The ID of the project the label belongs to.
            label_id (str): The ID of the label to delete.

        Returns:
            Dict[str, Any]: A message indicating the result of the deletion.
        """
        result = self.call_api_delete(f"projects/{project_id}/labels/{label_id}/")
        if result.ok:
            return {"message": "Label deleted successfully."}
        return result.json()

    # Member methods (don't work in TAC)
    # def get_workspace_members(self):
    #     return self.call_api_get("members").json()

    # def get_project_members(self, project_id: str):
    #     return self.call_api_get(f"projects/{project_id}/members/").json()

    # Module methods
    def create_module(
        self, project_id: str, module_data: ModuleCreate
    ) -> Dict[str, Any]:
        """Create a new module.

        Args:
            project_id (str): The ID of the project to create the module in.
            module_data (ModuleCreate): The data for the new module.

        Returns:
            Dict[str, Any]: The created module's data.
        """
        if isinstance(module_data, dict):
            module_data = ModuleCreate(**module_data)
        return self.call_api_post(
            f"projects/{project_id}/modules/",
            module_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def list_modules(self, project_id: str) -> List[Dict[str, Any]]:
        """List all modules in a project.

        Args:
            project_id (str): The ID of the project to list modules for.

        Returns:
            List[Dict[str, Any]]: A list of modules in the project.
        """
        result = self.call_api_get(f"projects/{project_id}/modules/").json()
        return result.get("results", [])

    def get_module(self, project_id: str, module_id: str) -> Dict[str, Any]:
        """Get details of a specific module.

        Args:
            project_id (str): The ID of the project the module belongs to.
            module_id (str): The ID of the module to retrieve.

        Returns:
            Dict[str, Any]: The details of the module.
        """
        return self.call_api_get(f"projects/{project_id}/modules/{module_id}/").json()

    def update_module(
        self, project_id: str, module_id: str, module_data: Module
    ) -> Dict[str, Any]:
        """Update an existing module.

        Args:
            project_id (str): The ID of the project the module belongs to.
            module_id (str): The ID of the module to update.
            module_data (Module): The updated data for the module.

        Returns:
            Dict[str, Any]: The updated module's data.
        """
        if isinstance(module_data, dict):
            module_data = Module(**module_data)
        return self.call_api_patch(
            f"projects/{project_id}/modules/{module_id}/",
            module_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def delete_module(self, project_id: str, module_id: str) -> Dict[str, Any]:
        """Delete a module.

        Args:
            project_id (str): The ID of the project the module belongs to.
            module_id (str): The ID of the module to delete.

        Returns:
            Dict[str, Any]: The result of the API call.
        """
        result = self.call_api_delete(f"projects/{project_id}/modules/{module_id}/")
        if result.ok:
            return {"message": "Module deleted successfully."}
        return result.json()

    # Module-Issue methods
    def list_module_issues(
        self, project_id: str, module_id: str
    ) -> List[Dict[str, Any]]:
        """List all issues in a module.

        Args:
            project_id (str): The ID of the project the module belongs to.
            module_id (str): The ID of the module to list issues for.

        Returns:
            List[Dict[str, Any]]: A list of issues in the module.
        """
        result = self.call_api_get(
            f"projects/{project_id}/modules/{module_id}/module-issues/"
        ).json()
        return result.get("results", [])

    def add_module_issue(
        self, project_id: str, module_id: str, issues: List[str]
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Add issues to a module.

        Args:
            project_id (str): The ID of the project the module belongs to.
            module_id (str): The ID of the module to add issues to.
            issues (List[str]): A list of issue IDs to add to the module.

        Returns:
            List[Dict[str, Any]] | Dict[str, Any]: The result of the API call. If successful, returns a list of issues in the module; otherwise, returns an error message.
        """
        return self.call_api_post(
            f"projects/{project_id}/modules/{module_id}/module-issues/",
            {"issues": issues},
        ).json()

    def delete_module_issue(
        self, project_id: str, module_id: str, issue_id: str
    ) -> Dict[str, Any]:
        """Remove an issue from a module.

        Args:
            project_id (str): The ID of the project the module belongs to.
            module_id (str): The ID of the module to remove the issue from.
            issue_id (str): The ID of the issue to remove from the module.

        Returns:
            Dict[str, Any]: The result of the API call.
        """
        result = self.call_api_delete(
            f"projects/{project_id}/modules/{module_id}/module-issues/{issue_id}/"
        )
        if result.ok:
            return {"message": "Issue removed from module successfully."}
        return result.json()

    # Cycle methods
    def create_cycle(self, project_id: str, cycle_data: CycleCreate) -> Dict[str, Any]:
        """Create a new cycle.

        Args:
            project_id (str): The ID of the project to create the cycle in.
            cycle_data (CycleCreate): The data for the new cycle.

        Returns:
            Dict[str, Any]: The details of the created cycle.
        """
        if isinstance(cycle_data, dict):
            cycle_data = CycleCreate(**cycle_data)
        return self.call_api_post(
            f"projects/{project_id}/cycles/",
            cycle_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def list_cycles(self, project_id: str) -> List[Dict[str, Any]]:
        """List all cycles in a project.

        Args:
            project_id (str): The ID of the project to list cycles for.

        Returns:
            List[Dict[str, Any]]: A list of cycles in the project.
        """
        result = self.call_api_get(f"projects/{project_id}/cycles/").json()
        return result.get("results", [])

    def get_cycle(self, project_id: str, cycle_id: str) -> Dict[str, Any]:
        """Get details of a specific cycle.

        Args:
            project_id (str): The ID of the project the cycle belongs to.
            cycle_id (str): The ID of the cycle to retrieve.

        Returns:
            Dict[str, Any]: The details of the cycle.
        """
        return self.call_api_get(f"projects/{project_id}/cycles/{cycle_id}/").json()

    def update_cycle(
        self, project_id: str, cycle_id: str, cycle_data: Cycle
    ) -> Dict[str, Any]:
        """Update cycle details.

        Args:
            project_id (str): The ID of the project the cycle belongs to.
            cycle_id (str): The ID of the cycle to update.
            cycle_data (Cycle): The updated cycle data.

        Returns:
            Dict[str, Any]: The details of the updated cycle.
        """
        if isinstance(cycle_data, dict):
            cycle_data = Cycle(**cycle_data)
        return self.call_api_patch(
            f"projects/{project_id}/cycles/{cycle_id}/",
            cycle_data.model_dump(exclude_unset=True, mode="json"),
        ).json()

    def delete_cycle(self, project_id: str, cycle_id: str) -> Dict[str, Any]:
        """Delete a cycle.

        Args:
            project_id (str): The ID of the project the cycle belongs to.
            cycle_id (str): The ID of the cycle to delete.

        Returns:
            Dict[str, Any]: The result of the API call.
        """
        result = self.call_api_delete(f"projects/{project_id}/cycles/{cycle_id}/")
        if result.ok:
            return {"message": "Cycle deleted successfully."}
        return result.json()

    # Cycle-Issue methods
    def list_cycle_issues(self, project_id: str, cycle_id: str) -> List[Dict[str, Any]]:
        """List all issues in a cycle.

        Args:
            project_id (str): The ID of the project the cycle belongs to.
            cycle_id (str): The ID of the cycle to list issues for.

        Returns:
            List[Dict[str, Any]]: A list of issues in the cycle.
        """
        result = self.call_api_get(
            f"projects/{project_id}/cycles/{cycle_id}/cycle-issues/"
        ).json()
        return result.get("results", [])

    def add_cycle_issue(
        self, project_id: str, cycle_id: str, issues: List[str]
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Add issues to a cycle.

        Args:
            project_id (str): The ID of the project the cycle belongs to.
            cycle_id (str): The ID of the cycle to add issues to.
            issues (List[str]): A list of issue IDs to add to the cycle.

        Returns:
            List[Dict[str, Any]] | Dict[str, Any]: The result of the API call. If successful, returns a list of issues in the cycle; otherwise, returns an error message.
        """
        return self.call_api_post(
            f"projects/{project_id}/cycles/{cycle_id}/cycle-issues/",
            {"issues": issues},
        ).json()

    # TODO: this method returns 404, needs investigation
    def delete_cycle_issue(
        self, project_id: str, cycle_id: str, issue_id: str
    ) -> Dict[str, Any]:
        """Delete an issue from a cycle.

        Args:
            project_id (str): The ID of the project the cycle belongs to.
            cycle_id (str): The ID of the cycle to delete the issue from.
            issue_id (str): The ID of the issue to delete from the cycle.

        Returns:
            Dict[str, Any]: The result of the API call.
        """
        result = self.call_api_delete(
            f"projects/{project_id}/cycles/{cycle_id}/cycle-issues/{issue_id}/"
        )
        if result.ok:
            return {"message": "Issue removed from cycle successfully."}
        return result.json()

    # New FRONTNED methods
    def list_workspace_members(self) -> List[Dict[str, Any]]:
        """List all members in the current workspace.

        Returns:
            List[Dict[str, Any]]: A list of members in the workspace.
        """
        result = self.req.get(
            f"{self.server_url}/api/workspaces/{self.workspace}/members/"
        ).json()
        members = []
        for member in result:  # parse only relevant data
            member_data = member.get("member")  # weird nested structure
            member_data.update(
                {
                    "role": member.get("role"),
                    "created_at": member.get("created_at"),
                }
            )
            members.append(member_data)
        return members

    def get_project_members(self, project_id: str) -> List[Dict[str, Any]]:
        """List all members in a specific project.

        Args:
            project_id (str): The ID of the project to list members for.

        Returns:
            List[Dict[str, Any]]: A list of members in the project.
        """
        result = self.req.get(
            f"{self.server_url}/api/workspaces/{self.workspace}/projects/{project_id}/members/"
        ).json()
        return result

    def add_project_members(
        self, project_id: str, member_ids: List[str], role: int = 15
    ) -> List[Dict[str, Any]]:
        """Add members to a specific project.

        Args:
            project_id (str): The ID of the project to add the member to.
            member_ids (List[str]): The IDs of the members to add.
            role (int): The role to assign to the new members (5 - guest, 10 - viewer, 15 - member). Defaults to 15.

        Returns:
            List[Dict[str, Any]]: The details of the added members.
        """
        body = {
            "members": [
                {"member_id": member_id, "role": role} for member_id in member_ids
            ]
        }
        return self.req.post(
            f"{self.server_url}/api/workspaces/{self.workspace}/projects/{project_id}/members/",
            json=body,
        ).json()

    def delete_project(self, project_id: str) -> Dict[str, str]:
        """Delete a project.

        Args:
            project_id (str): The ID of the project to delete. Can be both ID or readable identifier. Preferably ID.

        Returns:
            Dict[str, str]: feedback message about the deletion status.
        """
        result = self.req.delete(
            f"{self.server_url}/api/workspaces/{self.workspace}/projects/{project_id}/"
        )
        if result.ok:
            return {"message": "Project deleted successfully."}
        return result.json()
