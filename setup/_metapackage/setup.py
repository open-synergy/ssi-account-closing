import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-account-closing",
    description="Meta package for open-synergy-ssi-account-closing Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_account_closing',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
