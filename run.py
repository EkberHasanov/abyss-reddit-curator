import os

from service import generate_content


def main():
    input_value = os.environ.get('input_value', 'default_value')
    result = generate_content(input_value)
    with open('output/result.txt', 'w') as f:
        f.write(result)


if __name__ == "__main__":
    main()
