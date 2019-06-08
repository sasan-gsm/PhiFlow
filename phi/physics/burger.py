from .physics import *
from phi.math import *
from .domain import *


class Burger(VolumetricPhysics):

    def __init__(self, domain, viscosity=0.1, world=world, dt=1.0):
        VolumetricPhysics.__init__(self, domain, world, dt)
        self.viscosity = viscosity
        world.add(self)

    def step(self, velocity):
        return self.advect(self.diffuse(velocity))

    def _update_domain(self):
        mask = 1 - geometry_mask(self.world, self.domain.grid, 'obstacle')
        self.domainstate = DomainState(self.domain, self.world.state, active=mask, accessible=mask)

    def shape(self, batch_size=1):
        return self.grid.shape(self.rank, batch_size=batch_size)

    def serialize_to_dict(self):
        return {
            'type': 'burger',
            'class': self.__class__.__name__,
            'module': self.__class__.__module__,
            'rank': self.domain.rank,
            'domain': self.domain.serialize_to_dict(),
            'viscosity': self.viscosity,
        }

    def advect(self, velocity):
        idx = indices_tensor(velocity)
        velocity = velocity[..., ::-1]
        sample_coords = idx - velocity * self.dt
        result = math.resample(velocity, sample_coords, interpolation='linear', boundary='REPLICATE')
        return result

    def diffuse(self, velocity):
        return velocity + self.viscosity * vector_laplace(velocity)


def vector_laplace(v):
    return np.concatenate([laplace(v[...,i:i+1]) for i in range(v.shape[-1])], -1)