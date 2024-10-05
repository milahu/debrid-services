{
  pkgs ? import <nixpkgs> { },
  #pkgs ? import ./. {}
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    gnumake
    (python3.withPackages (pp: with pp; [
      requests
      beautifulsoup4
      aiohttp
      black
    ]))
  ];
}
