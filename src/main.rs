#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]

use std::{env, path};
use std::path::Path;
use std::{fs::File, io::Read};
use sha2::{Sha256, Digest};
use anyhow::Result;
// use walkdir::WalkDir;
use clap::{arg, command, value_parser, ArgAction, Command};

/// Computes the sha256 of a file
fn compute_sha_256(file: &str) -> Result<String> {
    let mut file = File::open(file)?;

    let mut hasher = Sha256::new();

    let mut buffer = [0; 4096];
    loop {
        let bytes_read = file.read(&mut buffer)?;
        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
    }

    Ok(format!("{:x}", hasher.finalize()))
}

fn get_files_in_path(path: &str) {
    return ();
}


/// Prints the current working directory
/// Useful for testing purposes
fn pwd() -> std::io::Result<()> {
    let current_directory = env::current_dir()?;
    println!("\n{}", current_directory.display());
    Ok(())
}

/// Changes from current directory to `root`
/// Analogous to the `cd` command found in Linux and MacOS
fn cd(root: &str) {
    let root = Path::new(root);
    assert!(env::set_current_dir(&root).is_ok());
}


fn main() {
    let matches = Command::new("Doopie")
        .version("1.0")
        .author("Brandon Jose Tenorio Noguera <bjtnoguera@gmail.com>")
        .about("Doopie is a command line tool to find duplicate files in a directory")
        .arg(arg!(--directory <PATH>).required(true))
        .arg(arg!(--ignore <FILE>).required(false))
        .arg(arg!(--regex <STRING>).required(false))
        .get_matches();

    let _ = pwd();

    let directory: String = matches.get_one::<String>("directory")
        .expect("required")
        .to_string();

    let _ = cd(&directory);

    let _ = pwd();
}
