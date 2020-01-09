import sys

from ast import (
    Import,
    ImportFrom,
    Module,
    parse,
    stmt as Statement,
)
from itertools import (
    islice,
)
from operator import (
    attrgetter,
)
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Type,
    Union,
)


ImportStatement = Union[Import, ImportFrom]


class ImportedItem:
    def __init__(
            self,
            name: str,
            alias: Optional[str] = None
    ) -> None:
        self.name: str = name
        self.alias: Optional[str] = alias


class AbstractImportProxy:
    def __init__(self, statement: ImportStatement) -> None:
        self.items: Set[ImportedItem] = {
            ImportedItem(item.name, item.asname)
            for item in statement.names
        }

    def pretty_str(self) -> str:
        raise NotImplementedError


class ImportProxy(AbstractImportProxy):
    def pretty_str(self) -> str:
        assert len(self.items) == 1
        item = next(iter(self.items))
        alias = ''
        if item.alias:
            alias = ' as {item.alias}'
        result = f'import {item.name}{alias}'
        return result


class ImportFromProxy(AbstractImportProxy):
    def __init__(self, statement: ImportFrom) -> None:
        super().__init__(statement)
        self.module = statement.module

    def pretty_str(self) -> str:
        sorted_items = sorted(
            self.items,
            key=attrgetter('name'),
        )
        verbose_items: List[str] = []
        for item in sorted_items:
            alias = ''
            if item.alias:
                alias = f' as {item.alias}'
            verbose_item = f'    {item.name}{alias},'
            verbose_items.append(verbose_item)

        result = 'from {module} import (\n{items}\n)'.format(
            module=self.module,
            items='\n'.join(verbose_items)
        )

        return result


class ImportsListProxy:
    def __init__(self) -> None:
        self.items: List[AbstractImportProxy] = []

    def append(self, item: AbstractImportProxy) -> None:
        pass


PROXY_BY_TYPE: Dict[Type[Statement], Type[AbstractImportProxy]] = {
    Import: ImportProxy,
    ImportFrom: ImportFromProxy,
}


def get_imports(file_path: str) -> ImportsListProxy:
    with open(file_path, 'rt') as file:
        content: str = file.read()
        module: Module = parse(content)

        proxies = ImportsListProxy()
        for statement in module.body:
            statement_type = type(statement)
            proxy_type = PROXY_BY_TYPE.get(statement_type)
            if proxy_type is not None:
                proxy = proxy_type(statement)
                proxies.append(proxy)

        return proxies


def prettify_file(file_path: str) -> None:
    imports: ImportsListProxy = get_imports(
        file_path,
    )


def main(argv: List[str]) -> None:
    """
    Принимает на вход список путей к py-файлам, у
    которых нужно отформатировать импорты.
    """
    files_to_prettify = islice(argv, 1, None)
    for file_path in files_to_prettify:
        prettify_file(file_path)


if __name__ == '__main__':
    main(sys.argv)
