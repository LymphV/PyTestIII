import click



@click.command()
@click.option('--hash-type', 'ht',
              type=click.Choice(['MD5', 'SHA1'], case_sensitive=False))
def main (ht):
    print (ht)
    
    
if __name__ == '__main__':
    main ()