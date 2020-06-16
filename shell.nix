{ pkgs ? import<nixpkgs> {} }:

with pkgs;
mkShell {
	SHELL_NAME = "GalaxyTools";
	buildInputs = [ perl perlPackages.DevelNYTProf ];
}
