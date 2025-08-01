with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python311
    python311Packages.django
    python311Packages.gunicorn
    python311Packages.psycopg2
    python311Packages.sqlparse
    python311Packages.whitenoise
    python311Packages.pip
    python311Packages.setuptools
  ];
}
