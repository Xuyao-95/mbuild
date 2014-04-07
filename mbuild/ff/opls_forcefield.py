import os
import pdb

import mbuild
from mbuild.prototype import Prototype
import mbuild.unit as units
from mbuild.decorators import *
from mbuild.ff.atom_type import Atomtype


class OplsForceField(object):
    """A container class for the OPLS forcefield."""

    def __init__(self):
        """Populate the database using files bundled with GROMACS."""
        self.atom_types = dict()
        self.bond_types = dict()
        self.angle_types = dict()
        self.dihedral_types = dict()

        # GROMACS specific units
        self.MASS = units.amu
        self.CHARGE = units.elementary_charge
        self.DIST = units.nanometers
        self.ENERGY = units.kilojoules_per_mole

        nonbonded_file = os.path.join(mbuild.__path__[0], 'ff', 'ffnonbonded_processed.itp')
        with open(nonbonded_file, 'r') as f:
            for line in f:
                if line.strip():
                    fields = line.split()
                    if fields[0][0] in [';', '[', '#']:
                        continue
                    self.add_atom_type(fields[0],
                            fields[1],
                            int(fields[2]),
                            fields[3] * self.MASS,
                            fields[4] * self.CHARGE,
                            #fields[5]  #  ignore ptype
                            fields[6] * self.DIST,
                            fields[7] * self.ENERGY)

        parsable_keywords = {'[ bondtypes ]': self.parse_bond_types,
                '[ angletypes ]': self.parse_angle_types,
                '[ dihedraltypes ]': self.parse_dihedral_types}
        bonded_file = os.path.join(mbuild.__path__[0], 'ff', 'ffbonded_processed.itp')
        with open(bonded_file, 'r') as f_bonded:
            for line in f_bonded:
                if line.strip():
                    keyword = line.strip()
                    fields = line.split()
                    if fields[0][0] in [';', '#']:
                        continue
                    elif keyword in parsable_keywords:
                        parsable_keywords[keyword](f_bonded)

    def parse_bond_types(self, f_bonded):
        """Read bond parameter information."""
        for line in f_bonded:
            if not line.strip():
                break
            fields = line.split()
            if fields[0][0] in [';', '#']:
                continue
            pair = (fields[0], fields[1])
            if int(fields[2]) == 1:
                r = float(fields[3]) * self.DIST
                k = float(fields[3]) * self.ENERGY / (self.DIST * self.DIST)
            self.bond_types[pair] = (r.in_units_of(units.angstroms), k)

    def parse_angle_types(self, f_bonded):
        """Read angle parameter information."""
        for line in f_bonded:
            if not line.strip():
                break
            fields = line.split()
            if fields[0][0] in [';', '#']:
                continue
            triplet = (fields[0], fields[1], fields[2])
            self.angle_types[triplet] = [float(field) for field in fields[4:6]]

    def parse_dihedral_types(self, f_bonded):
        """Read dihedral parameter information."""
        for line in f_bonded:
            if not line.strip():
                break
            fields = line.split()
            if fields[0][0] in [';', '#']:
                continue
            if ';' in fields:
                end_of_params = fields.index(';')
            else:
                end_of_params = len(fields)

            quartet = (fields[0], fields[1], fields[2], fields[3])
            self.dihedral_types[quartet] = fields[5:end_of_params]



    def get_atom_types(self, compound):
        """Parameterize a compound with atom specific information."""
        for atom in compound.atoms():
            if atom.kind in self.atom_types:
                params = self.atom_types[atom.kind]
                Prototype(atom.kind,
                        bond_type=params.alias,
                        atomic_num=params.atomic_number,
                        mass=params.mass,
                        charge=params.charge,
                        sigma=params.sigma,
                        epsilon=params.epsilon)

    def findAtomTypes(self, atom_id):
        # if the id is the atom type, return the AtomType object
        if atom_id in self.atom_types:
            return [self.atom_types[atom_id]]

        matching_atom_types = []

        for opls_type, atom_type in self.atom_types.iteritems():

            if str(atom_id).endswith('*'):
                # id is a wildcard ending in *
                prefix = str(atom_id)[:-1]

                if atom_type.alias.startswith(prefix):
                    matching_atom_types.append(opls_type)
                elif opls_type.startswith(prefix):
                    matching_atom_types.append(opls_type)
            else:
                # id is not a wildcard
                if atom_id == atom_type.alias:
                    matching_atom_types.append(opls_type)

        # return the matching_atom_types
        return matching_atom_types

    @accepts_compatible_units(None, None, None,
            units.amu,
            units.elementary_charge,
            units.angstroms,
            units.kilojoules_per_mole / units.angstroms**(2))
    def add_atom_type(self, opls_type, bond_type=None, atomic_number=0,
            mass=0.0 * units.amu,
            charge=0.0 * units.elementary_charge,
            sigma=0.0 * units.angstroms,
            epsilon=0.0 * units.kilojoules_per_mole / units.angstroms**(2)):
        """
        """
        self.atom_types[opls_type] = Atomtype(kind=opls_type, alias=bond_type,
                atomic_number=atomic_number, mass=mass, charge=charge,
                sigma=sigma, epsilon=epsilon)

    @accepts_compatible_units(None,
            units.angstroms,
            units.kilojoules_per_mole * units.nanometers**(-2))
    def add_bond_type(self, pair, r, k):
        self.bond_types[pair] = (r, k)

if __name__ == "__main__":
    ff = OplsForceField()
    pdb.set_trace()