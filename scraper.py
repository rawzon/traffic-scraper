def git_commit_posted_file():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
        subprocess.run(["git", "add", POSTED_FILE], check=True)

        # Check for staged changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("📝 No changes to commit. Skipping commit and push.")
            return  # 🔕 Skip commit/push gracefully

        subprocess.run(["git", "commit", "-m", "Update posted messages list"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Changes committed and pushed.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"Unexpected Git error: {e}")
