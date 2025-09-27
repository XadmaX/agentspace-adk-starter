terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Default region"
  type        = string
  default     = "us-central1"
}

# Pub/Sub topics
resource "google_pubsub_topic" "context_updated" {
  name = "context.updated"
}

resource "google_pubsub_topic" "pr_opened" {
  name = "pr.opened"
}

resource "google_pubsub_topic" "test_run_requested" {
  name = "test.run.requested"
}

