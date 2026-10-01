# The smallest image that exercises the whole release pipeline (both architectures, load,
# boot, smoke test) in this repository's own CI, before any repository pins a new version.
FROM busybox:1.38@sha256:fd7dc98638c8e305f4dc34e979f1c0fdfdcaeb0fbf8fcff77ae834b6da3d7e6e
COPY index.html /www/index.html
EXPOSE 8080
CMD ["httpd", "-f", "-p", "8080", "-h", "/www"]
