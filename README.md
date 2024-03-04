isc-dhcp44-server dhcp6 parser, to use you are best reading the source, but basically:

  leases = d6lease.d6leases.load_leases()
  for ia_na in leases.ia_nas:
    print(ia_na)

There are other fields too to explore, and this parser was written stricly to comply with
my usecase, so the grammer will need to be expanded to fully support all the fields.
