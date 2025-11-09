"""
GitHub Manager Module for AI Scientists Simulation

This module provides GitHub API integration for managing research repositories,
pull requests, and code reviews in the AI scientists simulation.
"""

import os
import time
from typing import Dict, List, Optional, Tuple
from github import Github, Repository, PullRequest, GithubException
from github.GithubException import UnknownObjectException


class GitHubManager:
    """
    Manages GitHub repository operations including PR creation, review, and merging.
    """
    
    def __init__(self, access_token: str, repo_owner: str, repo_name: str):
        """
        Initialize GitHub Manager.
        
        Args:
            access_token: GitHub Personal Access Token
            repo_owner: GitHub username or organization name
            repo_name: Repository name
        """
        from github import Auth
        auth = Auth.Token(access_token)
        self.github = Github(auth=auth)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo: Optional[Repository.Repository] = None
        self.user = self.github.get_user()
        
    def create_repository(self, description: str = "AI Scientists Research Simulation", 
                         private: bool = False) -> Repository.Repository:
        """
        Create a new GitHub repository.
        
        Args:
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            Created repository object
        """
        try:
            # Check if repo already exists
            self.repo = self.user.get_repo(self.repo_name)
            print(f"Repository {self.repo_name} already exists")
            return self.repo
        except UnknownObjectException:
            # Create new repository
            self.repo = self.user.create_repo(
                name=self.repo_name,
                description=description,
                private=private,
                auto_init=True  # Initialize with README
            )
            print(f"Created repository: {self.repo.full_name}")
            time.sleep(2)  # Wait for repo to be fully initialized
            return self.repo
    
    def get_repository(self) -> Repository.Repository:
        """
        Get existing repository.
        
        Returns:
            Repository object
        """
        if self.repo is None:
            self.repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        return self.repo
    
    def initialize_directory_structure(self):
        """
        Initialize the research repository directory structure.
        Creates directories: hypotheses/, experiments/, models/, discussions/, papers/
        """
        directories = [
            "hypotheses",
            "experiments",
            "models",
            "discussions",
            "papers"
        ]
        
        repo = self.get_repository()
        
        for directory in directories:
            try:
                # Create .gitkeep file in each directory to preserve structure
                file_path = f"{directory}/.gitkeep"
                repo.create_file(
                    path=file_path,
                    message=f"Initialize {directory} directory",
                    content="",
                    branch="main"
                )
                print(f"Created directory: {directory}/")
                time.sleep(1)  # Avoid rate limiting
            except GithubException as e:
                if e.status == 422:  # File already exists
                    print(f"Directory {directory}/ already exists")
                else:
                    raise
    
    def create_branch(self, branch_name: str, source_branch: str = "main") -> str:
        """
        Create a new branch from source branch.
        
        Args:
            branch_name: Name of the new branch
            source_branch: Source branch name (default: main)
            
        Returns:
            Created branch name
        """
        repo = self.get_repository()
        
        try:
            # Get the source branch reference
            source = repo.get_branch(source_branch)
            
            # Create new branch
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            print(f"Created branch: {branch_name}")
            return branch_name
        except GithubException as e:
            if e.status == 422:  # Branch already exists
                print(f"Branch {branch_name} already exists")
                return branch_name
            else:
                raise
    
    def commit_file(self, file_path: str, content: str, commit_message: str, 
                   branch: str = "main", update: bool = False) -> Dict:
        """
        Commit a file to the repository.
        
        Args:
            file_path: Path to the file in the repository
            content: File content
            commit_message: Commit message
            branch: Target branch
            update: Whether this is an update to existing file
            
        Returns:
            Commit information dictionary
        """
        repo = self.get_repository()
        
        try:
            if update:
                # Get existing file to update
                contents = repo.get_contents(file_path, ref=branch)
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=contents.sha,
                    branch=branch
                )
            else:
                # Create new file
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
            
            print(f"Committed file: {file_path} on branch {branch}")
            return {
                "path": file_path,
                "branch": branch,
                "sha": result["commit"].sha,
                "message": commit_message
            }
        except GithubException as e:
            if e.status == 422 and not update:
                # File already exists, try updating
                return self.commit_file(file_path, content, commit_message, branch, update=True)
            else:
                raise
    
    def create_pull_request(self, title: str, body: str, head_branch: str, 
                           base_branch: str = "main") -> PullRequest.PullRequest:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description/body
            head_branch: Source branch (branch with changes)
            base_branch: Target branch (default: main)
            
        Returns:
            Created pull request object
        """
        repo = self.get_repository()
        
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch
        )
        
        print(f"Created PR #{pr.number}: {title}")
        return pr
    
    def get_pull_request(self, pr_number: int) -> PullRequest.PullRequest:
        """
        Get a pull request by number.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Pull request object
        """
        repo = self.get_repository()
        return repo.get_pull(pr_number)
    
    def get_pr_files(self, pr_number: int) -> List[Dict]:
        """
        Get files changed in a pull request.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            List of file information dictionaries
        """
        pr = self.get_pull_request(pr_number)
        files = []
        
        for file in pr.get_files():
            files.append({
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if hasattr(file, 'patch') else None
            })
        
        return files
    
    def get_pr_content(self, pr_number: int) -> Dict:
        """
        Get detailed content of a pull request including file contents.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Dictionary with PR details and file contents
        """
        repo = self.get_repository()
        pr = self.get_pull_request(pr_number)
        
        # Get file contents
        files_content = {}
        for file in pr.get_files():
            try:
                # Get file content from the PR branch
                content = repo.get_contents(file.filename, ref=pr.head.ref)
                files_content[file.filename] = content.decoded_content.decode('utf-8')
            except Exception as e:
                files_content[file.filename] = f"[Error reading file: {str(e)}]"
        
        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "head_branch": pr.head.ref,
            "base_branch": pr.base.ref,
            "files": files_content,
            "files_changed": pr.changed_files,
            "additions": pr.additions,
            "deletions": pr.deletions
        }
    
    def create_review(self, pr_number: int, body: str, event: str = "COMMENT",
                     comments: Optional[List[Dict]] = None) -> Dict:
        """
        Create a review on a pull request.
        
        Args:
            pr_number: Pull request number
            body: Review body/comment
            event: Review event type - "APPROVE", "REQUEST_CHANGES", or "COMMENT"
            comments: List of line-specific comments (optional)
            
        Returns:
            Review information dictionary
        """
        pr = self.get_pull_request(pr_number)
        
        # Validate event type
        valid_events = ["APPROVE", "REQUEST_CHANGES", "COMMENT"]
        if event not in valid_events:
            raise ValueError(f"Invalid event type. Must be one of: {valid_events}")
        
        # Create review
        review = pr.create_review(
            body=body,
            event=event,
            comments=comments or []
        )
        
        print(f"Created review on PR #{pr_number}: {event}")
        return {
            "id": review.id,
            "body": body,
            "event": event,
            "state": review.state,
            "pr_number": pr_number
        }
    
    def approve_pr(self, pr_number: int, comment: str = "LGTM! Approving this PR.") -> Dict:
        """
        Approve a pull request.
        
        Args:
            pr_number: Pull request number
            comment: Approval comment
            
        Returns:
            Review information dictionary
        """
        return self.create_review(pr_number, comment, "APPROVE")
    
    def reject_pr(self, pr_number: int, comment: str) -> Dict:
        """
        Reject/request changes on a pull request.
        
        Args:
            pr_number: Pull request number
            comment: Rejection reason/requested changes
            
        Returns:
            Review information dictionary
        """
        return self.create_review(pr_number, comment, "REQUEST_CHANGES")
    
    def add_pr_comment(self, pr_number: int, comment: str) -> Dict:
        """
        Add a comment to a pull request.
        
        Args:
            pr_number: Pull request number
            comment: Comment text
            
        Returns:
            Comment information dictionary
        """
        pr = self.get_pull_request(pr_number)
        issue_comment = pr.create_issue_comment(comment)
        
        return {
            "id": issue_comment.id,
            "body": comment,
            "pr_number": pr_number
        }
    
    def get_pr_reviews(self, pr_number: int) -> List[Dict]:
        """
        Get all reviews for a pull request.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            List of review dictionaries
        """
        pr = self.get_pull_request(pr_number)
        reviews = []
        
        for review in pr.get_reviews():
            reviews.append({
                "id": review.id,
                "user": review.user.login,
                "body": review.body,
                "state": review.state,
                "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None
            })
        
        return reviews
    
    def merge_pr(self, pr_number: int, commit_message: Optional[str] = None,
                merge_method: str = "merge") -> Dict:
        """
        Merge a pull request.
        
        Args:
            pr_number: Pull request number
            commit_message: Custom merge commit message (optional)
            merge_method: Merge method - "merge", "squash", or "rebase"
            
        Returns:
            Merge information dictionary
        """
        pr = self.get_pull_request(pr_number)
        
        # Check if PR is mergeable
        if not pr.mergeable:
            raise ValueError(f"PR #{pr_number} is not mergeable")
        
        # Merge the PR
        result = pr.merge(
            commit_message=commit_message,
            merge_method=merge_method
        )
        
        print(f"Merged PR #{pr_number}")
        return {
            "merged": result.merged,
            "message": result.message,
            "sha": result.sha
        }
    
    def close_pr(self, pr_number: int) -> None:
        """
        Close a pull request without merging.
        
        Args:
            pr_number: Pull request number
        """
        pr = self.get_pull_request(pr_number)
        pr.edit(state="closed")
        print(f"Closed PR #{pr_number}")
    
    def get_file_content(self, file_path: str, branch: str = "main") -> str:
        """
        Get content of a file from repository.
        
        Args:
            file_path: Path to file in repository
            branch: Branch name (default: main)
            
        Returns:
            File content as string
        """
        repo = self.get_repository()
        
        try:
            content = repo.get_contents(file_path, ref=branch)
            return content.decoded_content.decode('utf-8')
        except UnknownObjectException:
            raise FileNotFoundError(f"File {file_path} not found on branch {branch}")
    
    def list_pull_requests(self, state: str = "open") -> List[Dict]:
        """
        List pull requests in repository.
        
        Args:
            state: PR state - "open", "closed", or "all"
            
        Returns:
            List of PR information dictionaries
        """
        repo = self.get_repository()
        prs = []
        
        for pr in repo.get_pulls(state=state):
            prs.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "head_branch": pr.head.ref,
                "base_branch": pr.base.ref,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat()
            })
        
        return prs
    
    def delete_branch(self, branch_name: str) -> None:
        """
        Delete a branch from repository.
        
        Args:
            branch_name: Name of branch to delete
        """
        repo = self.get_repository()
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()
        print(f"Deleted branch: {branch_name}")

