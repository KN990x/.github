# The smallest image that exercises the whole release pipeline (both architectures, load,
# boot, smoke test) in this repository's own CI, before any repository pins a new version.
FROM busybox:1.37@sha256:bdf57e528e45e4433820e045b29b4597825a1c9e38353532d90a01445013f82e
COPY index.html /www/index.html
EXPOSE 8080
CMD ["httpd", "-f", "-p", "8080", "-h", "/www"]
