import click



@click.command()
@click.option('--hash-type', 'ht',
              type=click.Choice(['MD5', 'SHA1'], case_sensitive=False))
@click.option('-x',
              type=click.Choice({'1':'111', '3':'333'}, case_sensitive=False))
def main (ht, x):
    print (ht)
    print (x)
    
    
if __name__ == '__main__':
    main ()