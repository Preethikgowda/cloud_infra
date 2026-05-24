# AWS CLI Infrastructure

This project includes a production-style AWS infrastructure plan that is provisioned using AWS CLI and Bash.

Terraform is intentionally not used for this setup.

## Goal

Prepare AWS infrastructure for a future EKS-based deployment of IntelliWealth.

The infrastructure script creates only foundational infrastructure.

It does not create:

- EKS cluster
- RDS database
- Route53 records
- ACM certificates
- CloudFront
- CI/CD
- Kubernetes manifests
- Helm releases
- Monitoring stack
- Bedrock resources

## Region

```text
ap-south-1
```

Availability zones:

```text
ap-south-1a
ap-south-1b
```

## VPC

```text
Name: intelliwealth-prod-vpc
CIDR: 10.0.0.0/16
```

## Subnets

Public subnets:

```text
intelliwealth-prod-public-subnet-az1
10.0.1.0/24
ap-south-1a

intelliwealth-prod-public-subnet-az2
10.0.2.0/24
ap-south-1b
```

Private app subnets:

```text
intelliwealth-prod-private-app-subnet-az1
10.0.3.0/24
ap-south-1a

intelliwealth-prod-private-app-subnet-az2
10.0.4.0/24
ap-south-1b
```

Private database subnet:

```text
intelliwealth-prod-private-db-subnet-az1
10.0.5.0/24
ap-south-1a
```

## Internet And NAT

The script creates:

- One internet gateway.
- Two NAT gateways.
- One Elastic IP per NAT gateway.

NAT gateways are placed in public subnets so private app subnets can reach the internet for image pulls and package access.

## Route Tables

Public route table:

```text
0.0.0.0/0 -> Internet Gateway
```

Private app route table AZ1:

```text
0.0.0.0/0 -> NAT Gateway AZ1
```

Private app route table AZ2:

```text
0.0.0.0/0 -> NAT Gateway AZ2
```

Private database route table:

```text
Local VPC routing only
No public internet route
```

## EKS Preparation Tags

Public subnets:

```text
kubernetes.io/role/elb=1
karpenter.sh/discovery=intelliwealth-prod-eks
```

Private app subnets:

```text
kubernetes.io/role/internal-elb=1
karpenter.sh/discovery=intelliwealth-prod-eks
```

## Security Groups

### Bastion Security Group

Allows:

```text
SSH 22 from your personal public IP only
```

Does not allow:

```text
0.0.0.0/0 on SSH
```

### ALB Security Group

Allows:

```text
80 from 0.0.0.0/0
443 from 0.0.0.0/0
```

### EKS Node Security Group

Prepares future EKS worker node communication:

- Node-to-node communication.
- ALB to node traffic.
- Kubernetes node communication.

### PostgreSQL Security Group

Allows:

```text
5432 only from EKS node security group
```

No public database access is allowed.

## Bastion Host

The script creates:

```text
Name: intelliwealth-prod-bastion
AMI: Amazon Linux 2023
Instance type: t3.micro
Subnet: public az1
Public IP: enabled
```

## Where To Run The Script

Recommended:

```text
AWS CloudShell
```

You do not need to launch an EC2 instance to run the script.

CloudShell already has AWS CLI and Bash.

## Before Running

Check AWS identity:

```bash
aws sts get-caller-identity
```

Check region:

```bash
aws configure get region
```

Set region if needed:

```bash
export AWS_DEFAULT_REGION=ap-south-1
```

Check your EC2 key pair:

```bash
aws ec2 describe-key-pairs \
  --region ap-south-1 \
  --key-names Masternode
```

## Personal IP

The script uses your current public IP for SSH access to the bastion host:

```bash
curl https://checkip.amazonaws.com
```

The result is used as:

```text
YOUR_PUBLIC_IP/32
```

Example:

```text
49.37.10.25/32
```

## Cost Warning

NAT gateways and EC2 instances can incur AWS charges while running.

Delete unused infrastructure when no longer needed.
