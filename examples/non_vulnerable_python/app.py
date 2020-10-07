import yaml

def main():
    with open("example.yaml") as f:
        yaml.safe_load(f)

if __name__ == '__main__':
    main()
