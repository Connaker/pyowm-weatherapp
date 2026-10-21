terraform {
  #backend "local" {}
  backend "s3" {
    bucket = ""
    key    = ""
    region = "us-east-1"
  }
}
