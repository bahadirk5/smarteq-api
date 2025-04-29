class BaseRepository:
    model = None

    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)

    def list(self):
        return self.model.objects.all()

    def get(self, **kwargs):
        return self.model.objects.get(**kwargs)

    def update(self, pk, **kwargs):
        obj = self.model.objects.get(pk=pk)
        for attr, value in kwargs.items():
            setattr(obj, attr, value)
        obj.save()
        return obj

    def delete(self, pk):
        obj = self.model.objects.get(pk=pk)
        obj.delete()
        return obj
