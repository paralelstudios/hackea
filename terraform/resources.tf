variable "access_key" {}
variable "secret_key" {}

variable "region" {
  default = "us-east-1"
}

variable "domain" {
  type    = "string"
  default = "aidex.help"
}

variable "domain_www" {
  type    = "string"
  default = "www.aidex.help"
}

variable "domain_api" {
  type    = "string"
  default = "api.aidex.help"
}

variable "api_pub_ip" {
  type = "string"
}

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

resource "aws_s3_bucket" "aidex" {
  bucket = "${var.domain}"
  acl    = "public-read"

  website {
    index_document = "index.html"
  }
}

resource "aws_s3_bucket" "aidex_www" {
  bucket = "${var.domain_www}"
  acl    = "public-read"

  website {
    redirect_all_requests_to = "${var.domain}"
  }
}

resource "aws_route53_zone" "aidex" {
  name = "${var.domain}"
}

resource "aws_s3_bucket" "aidex-logs" {
  bucket = "aidex-api-logs"
}

resource "aws_route53_record" "alias" {
  zone_id = "${aws_route53_zone.aidex.zone_id}"
  name    = "${var.domain}"
  type    = "A"

  alias {
    zone_id                = "${aws_s3_bucket.aidex.hosted_zone_id}"
    name                   = "${aws_s3_bucket.aidex.website_domain}"
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "alias_www" {
  zone_id = "${aws_route53_zone.aidex.zone_id}"
  name    = "${var.domain_www}"
  type    = "A"

  alias {
    zone_id                = "${aws_s3_bucket.aidex.hosted_zone_id}"
    name                   = "${aws_s3_bucket.aidex.website_domain}"
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "alias_api" {
  zone_id = "${aws_route53_zone.aidex.zone_id}"
  name    = "${var.domain_api}"
  type    = "A"
  ttl     = "300"
  records = ["${var.api_pub_ip}"]
}
