# SageMaker AI Studio Infrastructure

This repository contains the AWS Cloud Development Kit (CDK) code to provision the foundational infrastructure for a SageMaker AI Studio environment.

## Deployed AWS Resources

This CDK application deploys the following core resources:

* **VPC (Virtual Private Cloud):** A secure and isolated network with public, private, and isolated subnets.
* **S3 Bucket:** A dedicated bucket for SageMaker data storage, configured with auto-deletion of objects for easy cleanup.
* **IAM Roles:** Necessary roles for SageMaker execution, VPC Flow Logs, and custom resource Lambda functions, ensuring secure permissions.
* **CloudWatch Log Groups:** For monitoring VPC Flow Logs and SageMaker activities.

---

## Prerequisites

Before you begin, ensure you have the following installed:

* **Node.js** (LTS recommended)
* **AWS CLI** configured with credentials for account `796973481044` in `eu-central-1`.
* **AWS CDK CLI** (`npm install -g aws-cdk`)

---

## Getting Started

1.  **Clone the Repository:**
    ```bash
    git clone [your-repo-url]
    cd [your-repo-name]
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    # or
    pip install -r requirements.txt # if using Python CDK
    ```

3.  **CDK Bootstrap (First-time setup per AWS account/region):**
    ```bash
    cdk bootstrap aws://796973481044/eu-central-1
    ```

4.  **Deploy the Infrastructure:**
    ```bash
    cdk deploy
    ```
    Review the proposed IAM changes and type `y` to confirm.

---

## Cleaning Up

To remove all deployed resources from your AWS account:

```bash
cdk destroy
