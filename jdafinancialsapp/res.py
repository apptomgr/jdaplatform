line=['one', 'two', 'three']

for idx, i in enumerate(line, 0):
    print(f"254: {idx} - {i} - {i.id}")
    if idx == 1:
        print('MODELNAME.objects.create(f"brut_{idx}"')
