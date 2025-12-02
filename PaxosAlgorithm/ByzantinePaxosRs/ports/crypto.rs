impl crypto {
    fn encrypt(data: &str, key: &str) -> String {
        // Simple XOR encryption for demonstration purposes
        data.chars()
            .zip(key.chars().cycle())
            .map(|(d, k)| ((d as u8) ^ (k as u8)) as char)
            .collect()
    }
    fn decrypt(data: &str, key: &str) -> String {
        // Simple XOR decryption (same as encryption)
        data.chars()
            .zip(key.chars().cycle())
            .map(|(d, k)| ((d as u8) ^ (k as u8)) as char)
            .collect()
    }
}


