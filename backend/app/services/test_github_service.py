from pprint import pprint

from app.services.github_service import GitHubService


OWNER = "thahir2005"
REPO = "forgeops-changeguard-demo"
PR_NUMBER = 1


def main():
    github = GitHubService()

    print("ForgeOps GitHub Integration")
    print("===========================")

    pr = github.get_pull_request(
        OWNER,
        REPO,
        PR_NUMBER,
    )

    print("\nPull Request")
    print("------------")
    print("Number:", pr["number"])
    print("Title:", pr["title"])
    print("State:", pr["state"])
    print("Author:", pr["user"]["login"])
    print("Base:", pr["base"]["ref"])
    print("Head:", pr["head"]["ref"])

    files = github.get_changed_files(
        OWNER,
        REPO,
        PR_NUMBER,
    )

    print("\nChanged Files")
    print("-------------")

    for file in files:
        print(
            f"{file['filename']} "
            f"({file['status']}) "
            f"+{file['additions']} "
            f"-{file['deletions']}"
        )

    diff = github.get_pull_request_diff(
        OWNER,
        REPO,
        PR_NUMBER,
    )

    print("\nDiff Retrieved")
    print("--------------")
    print("Characters:", len(diff))
    print()

    print(diff)


if __name__ == "__main__":
    main()
