# Using EOF in SSH Command Executor

The application supports EOF (End of File) transmission through SSH commands using Heredoc syntax.

## EOF Transmission Method

### Heredoc

Used for passing multiline text:

```bash
cat << EOF
Your multiline text
can contain multiple lines
and special characters
EOF
```

**In GUI**: Use the "Heredoc" button to insert template.

## 📋 Usage Examples

### Creating file with multiline content

```bash
cat << EOF > /tmp/test.txt
Line 1
Line 2
Line 3
EOF
```

### Passing data to grep

```bash
cat << EOF | grep "pattern"
line with pattern
regular line
another line with pattern
EOF
```

## GUI Functions

Available in graphical interface:

- **"Heredoc" button**: Inserts heredoc template
- **Multiline input field**: Supports heredoc constructions

## Hotkeys

- `Ctrl+Enter`: Execute command
- Heredoc button: Quick insertion of heredoc template

## Technical Information

The application automatically:

- Detects multiline commands
- Properly escapes special characters
- Uses `bash -c` for complex constructions
- Maintains compatibility with existing commands

## Important Notes

1. EOF must be on separate line in heredoc
2. Heredoc syntax requires proper indentation
3. Always test commands on safe systems

## Real-world Examples

### Creating configuration file

```bash
sudo cat << EOF > /etc/example.conf
# Configuration file
setting1=value1
setting2=value2
EOF
```

### Passing SQL query

```bash
mysql -u user -p database << EOF
SELECT * FROM table1;
UPDATE table2 SET field='value';
EOF
```

### Sending data through netcat

```bash
cat << EOF | nc -l 8080
HTTP/1.0 200 OK

Hello World
EOF
```
