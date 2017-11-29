import xml.etree.ElementTree as ET
import glob


def has_attibutes(button):
    return 'action' in button.attrib


def search_in_file(tree_root):
    list_buttons = []

    if tree_root:
        for child in tree_root:
            if 'commandButton' in child.tag:
                if not has_attibutes(child):
                    list_buttons.append(child)
            else:
                for grand_child in child.findall('.'):
                    list_buttons.extend(search_in_file(grand_child))

    return list_buttons


def get_files(root_path):
    return glob.iglob(root_path + '/**/*.xml', recursive=True)


def main():
    list_pages = get_files('source')
    dict_buttons = {}

    for page in list_pages:
        tree = ET.parse(page)

        list_buttons = search_in_file(tree.getroot())

        if list_buttons:
            page_name = page[page.rfind('\\') + 1::]
            dict_buttons[page_name] = list_buttons

    for key, item in dict_buttons.items():
        print('Page: {} - Buttons: {}'.format(key, len(item)))


if __name__ == '__main__':
    main()
