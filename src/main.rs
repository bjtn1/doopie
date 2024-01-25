#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]
// use std::env;
use std::{fs::File, io::Read};
use sha2::{Sha256, Digest};
use anyhow::Result;
// use walkdir::WalkDir;
use clap::{arg, command, value_parser, ArgAction, Command};

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


fn main() {
    let matches = Command::new("Doopie")
        .version("1.0")
        .author("Brandon Jose Tenorio Noguera <bjtnoguera@gmail.com>")
        .about("Doopie is a command line tool to find duplicate files in a directory")
        .arg(arg!(--directory <STRING>).required(true))
        .get_matches();

    let directory = matches.get_one::<String>("directory").expect("required");
    println!("Directory passed in is {directory}");

    // match compute_sha_256(file_path) {
    //     Ok(hash) => println!("{hash}"),
    //     Err(e) => println!("{e}"),
    // }

}
