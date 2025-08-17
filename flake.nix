# code-owner: @agoose77
# This flake sets up an FSH dev-shell that installs all the required
# packages for running deployer, and then installs the tool in the virtual environment
# It is not best-practice for the nix-way of distributing this code,
# but its purpose is to get an environment up and running.
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      inherit (pkgs) lib;

      python = pkgs.python313;
      packages =
        [
          python
        ]
        ++ (with pkgs; [
          cmake
          ninja
          gcc
          pre-commit
          # Infra packages
          nodejs
        ]);
      shellHook = ''
        # Unset leaky PYTHONPATH
        unset PYTHONPATH

        __hash=$(echo ${python.interpreter} | sha256sum)

        # Setup if not defined ####
        if [[ ! -f ".venv/$__hash" ]]; then
            __setup_env() {
                # Remove existing venv
                if [[ -d .venv ]]; then
                    rm -r .venv
                fi

                # Stand up new venv
                ${python.interpreter} -m venv .venv

                ".venv/bin/python" -m pip install --group develop

                # Add a marker that marks this venv as "ready"
                touch ".venv/$__hash"
            }

            __setup_env
        fi
        ###########################

        # Add src/ to PYTHONPATH. Normally, an editable install would
        # do this, but we can't install literary editably as it is 
        # already bootstrapped.
        export PYTHONPATH="$(git rev-parse --show-toplevel)/src/"

        # Activate venv
        source .venv/bin/activate
      '';
      env = lib.optionalAttrs pkgs.stdenv.isLinux {
        # Python uses dynamic loading for certain libraries.
        # We'll set the linker path instead of patching RPATH
        LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux2014;
      };
    in {
      devShell = pkgs.mkShell {
        inherit env packages shellHook;
      };
    });
}
