"""
Module contianing all transaction types
"""
from JumpscaleLib.clients.blockchain.rivine.types.signatures import Ed25519PublicKey
from JumpscaleLib.clients.blockchain.rivine.types.unlockconditions import SingleSignatureFulfillment, UnlockHashCondition,\
 LockTimeCondition, AtomicSwapCondition, AtomicSwapFulfillment, MultiSignatureCondition, FulfillmentFactory, UnlockCondtionFactory, MultiSignatureFulfillment
from JumpscaleLib.clients.blockchain.rivine.encoding import binary

from JumpscaleLib.clients.blockchain.rivine.utils import hash
from JumpscaleLib.clients.blockchain.rivine.types.unlockhash import UnlockHash
from JumpscaleLib.clients.blockchain.rivine.secrets import token_bytes
from JumpscaleLib.clients.blockchain.rivine.const import HASTINGS_TFT_VALUE

from JumpscaleLib.clients.blockchain.tfchain.encoding import binary as tfbinary
from JumpscaleLib.clients.blockchain.tfchain.types import network as tftnet
from JumpscaleLib.clients.blockchain.tfchain.types import signatures as tftsig
from JumpscaleLib.clients.blockchain.tfchain import const as tfconst

import base64
import json

DEFAULT_TRANSACTION_VERSION = 1
MINTERDEFINITION_TRANSACTION_VERSION = 128
COINCREATION_TRANSACTION_VERSION = 129
BOT_REGISTRATION_TRANSACTION_VERSION = 144
BOT_RECORD_UPDATE_TRANSACTION_VERSION = 145
BOT_NAME_TRANSFER_TRANSACTION_VERSION = 146
HASHTYPE_COINOUTPUT_ID = 'coinoutputid'
DEFAULT_MINERFEE = 100000000

class TransactionFactory:
    """
    A transaction factory class
    """

    @staticmethod
    def create_transaction(version):
        """
        Creates and return a transaction of the speicfied verion

        @param version: Version of the transaction
        """
        if version == 1:
            return TransactionV1()


    @staticmethod
    def from_json(txn_json):
        """
        Creates a new transaction object from a json formated string

        @param txn_json: JSON string, representing a transaction
        """
        txn_dict = json.loads(txn_json)
        if 'version' not in txn_dict:
            return None
 
        if txn_dict['version'] == DEFAULT_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in Default Transaction (v{})".format(DEFAULT_TRANSACTION_VERSION))
            txn = TransactionV1()
            txn_data = txn_dict['data']
            if 'coininputs' in txn_data:
                for ci_info in txn_data['coininputs']:
                    ci = CoinInput.from_dict(ci_info)
                    txn._coin_inputs.append(ci)
            if 'coinoutputs' in txn_data:
                for co_info in txn_data['coinoutputs']:
                    co = CoinOutput.from_dict(co_info)
                    txn._coins_outputs.append(co)
            if 'minerfees' in txn_data:
                for minerfee in txn_data['minerfees'] :
                    txn.add_minerfee(int(minerfee))
            return txn
              
        if txn_dict['version'] == MINTERDEFINITION_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in MinterDefinition Transaction")
            txn = TransactionV128()
            txn_data = txn_dict['data']
            if 'nonce' in txn_data:
                txn._nonce = base64.b64decode(txn_data['nonce'])
            if 'mintcondition' in txn_data:
                txn._mint_condition = UnlockCondtionFactory.from_dict(txn_data['mintcondition'])
            if 'mintfulfillment' in txn_data:
                txn._mint_fulfillment = FulfillmentFactory.from_dict(txn_data['mintfulfillment'])
            if 'minerfees' in txn_data:
                for minerfee in txn_data['minerfees']:
                    txn.add_minerfee(int(minerfee))
            if 'arbitrarydata' in txn_data:
                txn._data = base64.b64decode(txn_data['arbitrarydata'])
            return txn
   
        if txn_dict['version'] == COINCREATION_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in CoinCreation Transaction")
            txn = TransactionV129()
            txn_data = txn_dict['data']
            if 'nonce' in txn_data:
                txn._nonce = base64.b64decode(txn_data['nonce'])
            if 'mintfulfillment' in txn_data:
                txn._mint_fulfillment = FulfillmentFactory.from_dict(txn_data['mintfulfillment'])
            if 'coinoutputs' in txn_data:
                for co_info in txn_data['coinoutputs']:
                    co = CoinOutput.from_dict(co_info)
                    txn._coin_outputs.append(co)
            if 'minerfees' in txn_data:
                for minerfee in txn_data['minerfees']:
                    txn.add_minerfee(int(minerfee))
            if 'arbitrarydata' in txn_data:
                txn._data = base64.b64decode(txn_data['arbitrarydata'])
            return txn

        if txn_dict['version'] == BOT_REGISTRATION_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in BotRegistration Transaction")
            txn = TransactionV144()
            txn.from_dict(txn_dict['data'])
            return txn

        if txn_dict['version'] == BOT_RECORD_UPDATE_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in BotRecordUpdate Transaction")
            txn = TransactionV145()
            txn.from_dict(txn_dict['data'])
            return txn

        if txn_dict['version'] == BOT_NAME_TRANSFER_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in BotNameTransfer Transaction")
            txn = TransactionV146()
            txn.from_dict(txn_dict['data'])
            return txn

class TransactionV1:
    """
    A Transaction is an atomic component of a block. Transactions can contain
	inputs and outputs and even arbitrar data. They can also contain signatures to prove that a given party has
	approved the transaction, or at least a particular subset of it.

	Transactions can depend on other previous transactions in the same block,
	but transactions cannot spend outputs that they create or otherwise beself-dependent.
    """
    def __init__(self):
        """
        Initializes a new tansaction
        """
        self._coin_inputs = []
        self._blockstakes_inputs = []
        self._coins_outputs = []
        self._blockstakes_outputs = []
        self._minerfees = []
        self._data = bytearray()
        self._version = bytearray([1])
        self._id = None

    @property
    def version(self):
        return 1

    @property
    def id(self):
        """
        Gets transaction id
        """
        return self._id

    @id.setter
    def id(self, txn_id):
        """
        Sets transaction id
        """
        self._id = txn_id

    @property
    def coin_inputs(self):
        """
        Retrieves coins inputs
        """
        return self._coin_inputs

    @property
    def coins_outputs(self):
        """
        Retrieves coins outputs
        """
        return self._coins_outputs


    @property
    def json(self):
        """
        Returns a json version of the TransactionV1 object
        """
        result = {
            'version': binary.decode(self._version, type_=int),
            'data': {
                'coininputs': [input.json for input in self._coin_inputs],
                'coinoutputs': [output.json for output in self._coins_outputs],
                'minerfees': [str(fee) for fee in self._minerfees]
            }
        }
        if self._data:
            result['data']['arbitrarydata'] = base64.b64encode(self._data).decode('utf-8')
        return result



    def add_data(self, data):
        """
        Add data to the transaction
        """
        self._data.extend(data)


    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


    def add_atomicswap_input(self, parent_id, pub_key, secret=None):
        """
        Adds a new atomicswap input to the transaction
        An atomicswap input can be for refund or redeem purposes, if for refund no secret is needed, but if for redeem then
        a secret needs tp be provided
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = AtomicSwapFulfillment(pub_key=key, secret=secret)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


    def add_multisig_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))



    def add_coin_output(self, value, recipient, locktime=None):
        """
        Add a new coin output to the transaction

        @param value: Amout of coins
        @param recipient: The recipient address
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._coins_outputs.append(CoinOutput(value=value, condition=condition))



    def add_atomicswap_output(self, value, recipient, locktime, refund_address, hashed_secret):
        """
        Add a new atomicswap output to the transaction
        """
        condition = AtomicSwapCondition(sender=refund_address, reciever=recipient,
                                        hashed_secret=hashed_secret, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coins_outputs.append(coin_output)
        return coin_output


    def add_multisig_output(self, value, unlockhashes, min_nr_sig, locktime=None):
        """
        Add a new MultiSignature output to the transaction

        @param value: Value of the output in hastings
        @param unlockhashes: List of all unlock hashes which are authorised to spend this output by signing off
        @param min_nr_sig: Defines the amount of signatures required in order to spend this output
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes,
                                            min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coins_outputs.append(coin_output)
        return coin_output


    def add_minerfee(self, minerfee):
        """
        Adds a minerfee to the transaction
        """
        self._minerfees.append(minerfee)


    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []

        buffer = bytearray()
        # encode the transaction version
        buffer.extend(self._version)
        # encode the input index
        buffer.extend(binary.encode(input_index))

        # encode extra objects if exists
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))

        # encode the number of coins inputs
        buffer.extend(binary.encode(len(self._coin_inputs)))

        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(binary.encode(coin_input.parent_id, type_='hex'))

        # encode coin outputs
        buffer.extend(binary.encode(self._coins_outputs, type_='slice'))

        # encode the number of blockstakes
        buffer.extend(binary.encode(len(self._blockstakes_inputs)))
        # encode blockstack inputs parent_ids
        for bs_input in self._blockstakes_inputs:
            buffer.extend(binary.encode(bs_input.parent_id, type_='hex'))

        # encode blockstake outputs
        buffer.extend(binary.encode(self._blockstakes_outputs, type_='slice'))

        # encode miner fees
        buffer.extend(binary.encode(len(self._minerfees)))
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))

        # encode custom data_
        buffer.extend(binary.encode(self._data, type_='slice'))

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)


class TransactionV128:
    """
    Minter definition transaction class. This transaction type
    allows the current coin creators to redefine who has the ability to create coins.
    """
    def __init__(self):
        self._mint_fulfillment = None
        self._mint_condition = None
        self._minerfees = []
        self._data = bytearray()
        self._version = bytearray([128])
        self._id = None
        self._nonce = token_bytes(nbytes=8)
        self._specifier = bytearray(b'minter defin tx\0')

    @property
    def version(self):
        return 128

    @property
    def id(self):
        """
        Get transaction id
        """
        return self._id
    @id.setter
    def id(self, txn_id):
        """
        Set transaction id
        """
        self._id = txn_id


    @property
    def mint_condition(self):
        """
        Retrieve the new mint condition which will be set
        """
        return self._mint_condition


    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        return self._mint_fulfillment


    @property
    def json(self):
        """
        Returns a json representation of the transaction
        """
        result = {
                'version': binary.decode(self._version, type_=int),
                'data': {
                    'nonce': base64.b64encode(self._nonce).decode('utf-8'),
                    'mintfulfillment': self._mint_fulfillment.json if self._mint_fulfillment else '{}',
                    'mintcondition': self._mint_condition.json if self._mint_condition else '{}',
                    'minerfees': [str(fee) for fee in self._minerfees]
                }
        }
        if self._data:
            result['data']['arbitrarydata'] = base64.b64encode(self._data).decode('utf-8')
        return result

    def add_data(self, data):
        """
        Add data to the transaction
        """
        self._data.extend(data)


    def set_singlesig_mint_condition(self, minter_address, locktime=None):
        """
        Set the mint condition to a singlesig condition.
         @param minter_address: The address of the singlesig condition to set as new mint condition
        """
        unlockhash = UnlockHash.from_string(minter_address)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._mint_condition = condition


    def set_multisig_mint_condition(self, unlockhashes, min_nr_sig, locktime=None):
        """
        Set the mint condition to a multisig condition
         @param unlockhashes: The unlockhashes which can sign the multisig condition
        @param min_nr_sig: The minimum amount of signatures in order to fulfill the condition
        @param locktime: An optional time until which the condition cannot be fulfilled
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes, min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._mint_condition = condition

    def set_condition(self, condition):
        """
        Set a new premade minter condition
        """
        self._mint_condition = condition

    def add_minerfee(self, minerfee):
        """
        Adds a minerfee to the transaction
        """
        self._minerfees.append(minerfee)


    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode transaction version
        buffer.extend(self._version)
        # encode the specifier
        buffer.extend(self._specifier)
        # encode nonce
        buffer.extend(self._nonce)
         # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))
         # encode new mintcondition
        buffer.extend(binary.encode(self._mint_condition))
        # minerfee length
        buffer.extend(binary.encode(len(self._minerfees)))
        # actual minerfees
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))
        # arb data
        buffer.extend(binary.encode(self._data, type_='slice'))

        return hash(data=buffer)


class TransactionV129:
    """
    Coin creation transaction class. This transaction type allows the current
    coin creators to create new coins and spend them.
    """
    def __init__(self):
        self._mint_fulfillment = None
        self._nonce = token_bytes(nbytes=8)
        self._version = bytearray([129])
        self._id = None
        self._minerfees = []
        self._data = bytearray()
        self._coin_outputs = []
        self._specifier = bytearray(b'coin mint tx')
        self._specifier.extend([0,0,0,0])

    @property
    def version(self):
        return 129

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id

    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id

    @property
    def coin_outputs(self):
        """
        Retrieves the coin outputs
        """
        return self._coin_outputs

    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        return self._mint_fulfillment

    @property
    def json(self):
        """
        Returns a json version of the TransactionV129 object
        """
        result = {
            'version': binary.decode(self._version, type_=int),
            'data': {
                'nonce': base64.b64encode(self._nonce).decode('utf-8'),
                'mintfulfillment': self._mint_fulfillment.json if self._mint_fulfillment else '{}',
                'coinoutputs': [output.json for output in self._coin_outputs],
                'minerfees': [str(fee) for fee in self._minerfees]
            }
        }
        if self._data:
            result['data']['arbitrarydata'] = base64.b64encode(self._data).decode('utf-8')
        return result

    def add_data(self, data):
        """
        Add data to the transaction
        """
        self._data.extend(data)

    def add_coin_output(self, value, recipient, locktime=None):
        """
        Add a new coin output to the transaction

        @param value: Amount of coins
        @param recipient: The recipient address
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))

    def add_multisig_output(self, value, unlockhashes, min_nr_sig, locktime=None):
        """
        Add a new MultiSignature output to the transaction

        @param value: Value of the output in hastings
        @param unlockhashes: List of all unlockhashes which are authorised to spend this input
        @param min_nr_sig: The amount of signatures required to spend this output
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes, min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coin_outputs.append(coin_output)

    def add_output(self, value, condition):
        """
        Add a new output from a premade condition
        """
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))

    def add_minerfee(self, minerfee):
        """
        Adds a miner fee to the transaction
        """
        self._minerfees.append(minerfee)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: ignored
        """
        if extra_objects is None:
            extra_objects = []

        buffer = bytearray()
        # encode the transaction version
        buffer.extend(self._version)
        # specifier
        buffer.extend(self._specifier)
        # nonce
        buffer.extend(self._nonce)

        # arbitrary objects if any
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))

        # new coin outputs
        buffer.extend(binary.encode(self._coin_outputs, type_='slice'))

        # miner fees
        buffer.extend(binary.encode(len(self._minerfees)))
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))

        # finally custom data
        buffer.extend(binary.encode(self._data, type_='slice'))

        return hash(data=buffer)

class TransactionV144:
    """
    Bot Registration transaction class. This transaction type allows a
    new 3Bot to be registered.
    """
    def __init__(self):
        self._specifier = bytearray(b'bot register tx\0')
        self._id = None
        self._addresses = []
        self._names = []
        self._number_of_months = 0
        self._transaction_fee = None
        self._coin_inputs = []
        self._refund_coin_output = None
        self._identification = None
    
    @property
    def version(self):
        return BOT_REGISTRATION_TRANSACTION_VERSION

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id
    
    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id

    @property
    def required_bot_fees(self):
        # a static registration fee has to be paid
        fees = tfconst.BOT_REGISTRATION_FEE_MULTIPLIER * HASTINGS_TFT_VALUE
        # the amount of desired months also has to be paid
        fees += _compute_monthly_bot_fees(self._number_of_months)
        # if more than one name is defined it also has to be paid
        lnames = len(self._names)
        if lnames > 1:
            fees += HASTINGS_TFT_VALUE * (lnames-1) * tfconst.BOT_FEE_PER_ADDITIONAL_NAME_MULTIPLIER
        # no fee has to be paid for the used network addresses during registration
        # return the total fees
        return fees

    @property
    def coin_inputs(self):
        """
        Retrieves coin inputs
        """
        return self._coin_inputs

    @property
    def json(self):
        """
        Returns a json version of the TransactionV144 object
        """
        result = {
            'version': self.version,
            'data': {
                'nrofmonths': self._number_of_months,
                'txfee': str(self._transaction_fee),
                'coininputs': [ci.json for ci in self._coin_inputs],
                'identification': self._identification.json,
            }
        }
        if self._addresses:
            result['data']['addresses'] = [addr.json for addr in self._addresses]
        if self._names:
            result['data']['names'] = self._names.copy()
        if self._refund_coin_output:
            result['data']['refundcoinoutput'] = self._refund_coin_output.json
        return result
    
    def from_dict(self, data):
        """
        Populates this TransactionV144 object from a data (JSON-decoded) dictionary
        """
        if 'nrofmonths' in data:
            self._number_of_months = data['nrofmonths']
        else:
            self._number_of_months = 0
        if 'txfee' in data:
            self._transaction_fee = int(data['txfee'])
        else:
            self._transaction_fee = None
        if 'coininputs' in data:
            for ci_info in data['coininputs']:
                ci = CoinInput.from_dict(ci_info)
                self._coin_inputs.append(ci)
        else:
            self._coin_inputs = []
        if 'identification' in data:
            self._identification = TfchainPublicKeySignaturePair.from_dict(data['identification'])
        else:
            self._identification = None
        if 'addresses' in data:
            for addr_str in data['addresses']:
                addr = tftnet.NetworkAddress.from_string(addr_str)
                self._addresses.append(addr)
        else:
            self._addresses = []
        if 'names' in data:
            self._names = data['names'].copy()
        else:
            self._names = []
        if 'refundcoinoutput' in data:
            co = CoinOutput.from_dict(data['refundcoinoutput'])
            self._refund_coin_output = co
        else:
            self._refund_coin_output = None

    def add_address(self, addr_str):
        addr = tftnet.NetworkAddress.from_string(addr_str)
        self._addresses.append(addr)
    
    def add_name(self, name):
        self._names.append(name)

    def set_transaction_fee(self, txfee):
        self._transaction_fee = txfee

    def set_number_of_months(self, n):
        if n < 1 or n > 24:
            ValueError("number of months for a 3Bot Registration Transaction has to be in the inclusive range [1,24]")
        self._number_of_months = n
    
    def set_public_key(self, key):
        self._identification = TfchainPublicKeySignaturePair(public_key=key, signature=None)

    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))
    
    def add_multisig_coin_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def set_refund_coin_output(self, value, recipient):
        """
        Set a coin output as refund coin output of this tx

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        self._refund_coin_output = CoinOutput(value=value, condition=condition)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode the transaction version
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self.version))
        # encode the specifier
        buffer.extend(self._specifier)

        # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(tfbinary.BinaryEncoder.encode(extra_object))

        # encode addresses
        buffer.extend(tfbinary.BinaryEncoder.encode(self._addresses, type_='slice'))
        # encode names
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names, type_='slice'))
        # encode number of months
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._number_of_months, _kind='int8'))

        # encode the number of coins inputs
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(len(self._coin_inputs), _kind='int'))
        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(tfbinary.BinaryEncoder.encode(coin_input.parent_id, type_='hex'))

        # encode transaction fee
        buffer.extend(binary.encode(self._transaction_fee, type_='currency'))
        # encode refund coin output
        if self._refund_coin_output:
            buffer.extend([1])
            buffer.extend(binary.encode(self._refund_coin_output))
        else:
            buffer.extend([0])
        # encode public key
        buffer.extend(tfbinary.BinaryEncoder.encode(self._identification.public_key))

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)

class TransactionV145:
    """
    Bot Record Update transaction class. This transaction type allows
    an existing 3Bot to be updated.
    """
    def __init__(self):
        self._specifier = bytearray(b'bot recupdate tx')
        self._id = None
        self._botid = None
        self._addresses_to_add = []
        self._addresses_to_remove = []
        self._names_to_add = []
        self._names_to_remove = []
        self._number_of_months = 0
        self._transaction_fee = None
        self._coin_inputs = []
        self._refund_coin_output = None
        self._signature = ''
        self._publickey = None
    
    @property
    def version(self):
        return BOT_RECORD_UPDATE_TRANSACTION_VERSION

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id
    
    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id

    @property
    def required_bot_fees(self):
        fees = 0
        # all additional months have to be paid
        if self._number_of_months > 0:
            fees += _compute_monthly_bot_fees(self._number_of_months)
        # a Tx that modifies the network address info of a 3bot record also has to be paid
        if self._addresses_to_add or self._addresses_to_remove:
            fees += tfconst.BOT_FEE_FOR_NETWORK_ADDRESS_INFO_CHANGE_MULTIPLIER * HASTINGS_TFT_VALUE
        # each additional name has to be paid as well
	    # (regardless of the fact that the 3bot has a name or not)
        lnames = len(self._names_to_add)
        if lnames > 0:
            fees += HASTINGS_TFT_VALUE * lnames * tfconst.BOT_FEE_PER_ADDITIONAL_NAME_MULTIPLIER
        # return the total fees
        return fees

    @property
    def coin_inputs(self):
        """
        Retrieves coin inputs
        """
        return self._coin_inputs

    @property
    def json(self):
        """
        Returns a json version of the TransactionV144 object
        """
        result = {
            'version': self.version,
            'data': {
                'id': self._botid,
                'nrofmonths': self._number_of_months,
                'txfee': str(self._transaction_fee),
                'coininputs': [ci.json for ci in self._coin_inputs],
                'signature': self._signature,
            }
        }
        addr_dic = {}
        if self._addresses_to_add:
            addr_dic['add'] = [addr.json for addr in self._addresses_to_add]
        if self._addresses_to_remove:
            addr_dic['remove'] = [addr.json for addr in self._addresses_to_remove]
        if len(addr_dic) > 0:
            result['data']['addresses'] = addr_dic
        name_dic = {}
        if self._names_to_add:
            name_dic['add'] = self._names_to_add.copy()
        if self._names_to_remove:
            name_dic['remove'] = self._names_to_remove.copy()
        if len(name_dic) > 0:
            result['data']['names'] = name_dic
        if self._refund_coin_output:
            result['data']['refundcoinoutput'] = self._refund_coin_output.json
        return result
    
    def from_dict(self, data):
        """
        Populates this TransactionV145 object from a data (JSON-decoded) dictionary
        """
        if 'id' in data:
            self._botid = data['id']
        else:
            self._botid = 0 # 0 is an invalid botID, the identifiers start at 1
        if 'nrofmonths' in data:
            self._number_of_months = data['nrofmonths']
        else:
            self._number_of_months = 0
        if 'txfee' in data:
            self._transaction_fee = int(data['txfee'])
        else:
            self._transaction_fee = None
        if 'coininputs' in data:
            for ci_info in data['coininputs']:
                ci = CoinInput.from_dict(ci_info)
                self._coin_inputs.append(ci)
        else:
            self._coin_inputs = []
        if 'signature' in data:
            self._signature = data['signature']
        else:
            self._signature = ''
        self._addresses_to_add = []
        self._addresses_to_remove = []
        if 'addresses' in data:
            if 'add' in data['addresses']:
                for addr_str in data['addresses']['add']:
                    addr = tftnet.NetworkAddress.from_string(addr_str)
                    self._addresses_to_add.append(addr)
            if 'remove' in data['addresses']:
                for addr_str in data['addresses']['remove']:
                    addr = tftnet.NetworkAddress.from_string(addr_str)
                    self._addresses_to_remove.append(addr)
        self._names_to_add = []
        self._names_to_remove = []
        if 'names' in data:
            if 'add' in data['names']:
                self._names_to_add = data['names']['add'].copy()
            if 'remove' in data['names']:
                self._names_to_remove = data['names']['remove'].copy()
        if 'refundcoinoutput' in data:
            co = CoinOutput.from_dict(data['refundcoinoutput'])
            self._refund_coin_output = co
        else:
            self._refund_coin_output = None

    def add_address_to_add(self, addr_str):
        addr = tftnet.NetworkAddress.from_string(addr_str)
        self._addresses_to_add.append(addr)

    def add_address_to_remove(self, addr_str):
        addr = tftnet.NetworkAddress.from_string(addr_str)
        self._addresses_to_remove.append(addr)
    
    def add_name_to_add(self, name):
        self._names_to_add.append(name)
    
    def add_name_to_remove(self, name):
        self._names_to_remove.append(name)

    def set_transaction_fee(self, txfee):
        self._transaction_fee = txfee

    def set_number_of_months(self, n):
        if n < 1 or n > 24:
            ValueError("number of months for a 3Bot Registration Transaction has to be in the inclusive range [1,24]")
        self._number_of_months = n
    
    def set_bot_id(self, identifier):
        self._botid = identifier
    
    def set_signature(self, signature):
        self._signature = signature

    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))
    
    def add_multisig_coin_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def set_refund_coin_output(self, value, recipient):
        """
        Set a coin output as refund coin output of this tx

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        self._refund_coin_output = CoinOutput(value=value, condition=condition)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode the transaction version
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self.version))
        # encode the specifier
        buffer.extend(self._specifier)
        # encode the bot identifier
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._botid, _kind='uint32'))

        # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(tfbinary.BinaryEncoder.encode(extra_object))

        # encode addresses
        buffer.extend(tfbinary.BinaryEncoder.encode(self._addresses_to_add, type_='slice'))
        buffer.extend(tfbinary.BinaryEncoder.encode(self._addresses_to_remove, type_='slice'))
        # encode names
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names_to_add, type_='slice'))
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names_to_remove, type_='slice'))
        # encode number of months
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._number_of_months, _kind='int8'))

        # encode the number of coins inputs
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(len(self._coin_inputs), _kind='int'))
        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(tfbinary.BinaryEncoder.encode(coin_input.parent_id, type_='hex'))

        # encode transaction fee
        buffer.extend(binary.encode(self._transaction_fee, type_='currency'))
        # encode refund coin output
        if self._refund_coin_output:
            buffer.extend([1])
            buffer.extend(binary.encode(self._refund_coin_output))
        else:
            buffer.extend([0])

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)

class TransactionV146:
    """
    Bot Name Transfer transaction class. This transaction type allows
    the transfer of one or multiple (bot) names between two existing 3 bots.
    """
    def __init__(self):
        self._specifier = bytearray(b'bot nametrans tx')
        self._id = None

        self._sender_botid = None
        self._sender_signature = ''
        self._receiver_botid = None
        self._receiver_signature = ''
        self._names = []

        self._transaction_fee = None
        self._coin_inputs = []
        self._refund_coin_output = None

        self._sender_publickey = None
        self._receiver_publickey = None

    @property
    def version(self):
        return BOT_NAME_TRANSFER_TRANSACTION_VERSION

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id
    
    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id

    @property
    def required_bot_fees(self):
        return HASTINGS_TFT_VALUE * len(self._names) * tfconst.BOT_FEE_PER_ADDITIONAL_NAME_MULTIPLIER

    @property
    def coin_inputs(self):
        """
        Retrieves coin inputs
        """
        return self._coin_inputs

    @property
    def json(self):
        """
        Returns a json version of the TransactionV144 object
        """
        result = {
            'version': self.version,
            'data': {
                'sender': {
                    'id': self._sender_botid,
                    'signature': self._sender_signature
                },
                'receiver': {
                    'id': self._receiver_botid,
                    'signature': self._receiver_signature
                },
                'names': self._names.copy(),
                'txfee': str(self._transaction_fee),
                'coininputs': [ci.json for ci in self._coin_inputs]
            }
        }
        if self._refund_coin_output:
            result['data']['refundcoinoutput'] = self._refund_coin_output.json
        return result
    
    def from_dict(self, data):
        """
        Populates this TransactionV146 object from a data (JSON-decoded) dictionary
        """
        sender_data = data.get('sender', {})
        self._sender_botid = sender_data.get('id', 0)
        self._sender_signature = sender_data.get('signature', '')
        receiver_data = data.get('receiver', {})
        self._sender_botid = receiver_data.get('id', 0)
        self._sender_signature = receiver_data.get('signature', '')
        if 'txfee' in data:
            self._transaction_fee = int(data['txfee'])
        else:
            self._transaction_fee = None
        if 'coininputs' in data:
            for ci_info in data['coininputs']:
                ci = CoinInput.from_dict(ci_info)
                self._coin_inputs.append(ci)
        else:
            self._coin_inputs = []
        self._names = []
        if 'names' in data:
            self._names = data['names'].copy()
        if 'refundcoinoutput' in data:
            co = CoinOutput.from_dict(data['refundcoinoutput'])
            self._refund_coin_output = co
        else:
            self._refund_coin_output = None

    def add_name(self, name):
        self._names.append(name)

    def set_transaction_fee(self, txfee):
        self._transaction_fee = txfee

    def set_sender_bot_id(self, identifier):
        self._sender_botid = identifier
    
    def set_sender_signature(self, signature):
        self._sender_signature = signature

    def set_receiver_bot_id(self, identifier):
        self._receiver_botid = identifier
    
    def set_receiver_signature(self, signature):
        self._receiver_signature = signature

    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))
    
    def add_multisig_coin_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def set_refund_coin_output(self, value, recipient):
        """
        Set a coin output as refund coin output of this tx

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        self._refund_coin_output = CoinOutput(value=value, condition=condition)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode the transaction version
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self.version))
        # encode the specifier
        buffer.extend(self._specifier)
        # encode the bot identifiers
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._sender_botid, _kind='uint32'))
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._receiver_botid, _kind='uint32'))

        # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(tfbinary.BinaryEncoder.encode(extra_object))

        # encode names
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names, type_='slice'))

        # encode the number of coins inputs
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(len(self._coin_inputs), _kind='int'))
        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(tfbinary.BinaryEncoder.encode(coin_input.parent_id, type_='hex'))

        # encode transaction fee
        buffer.extend(binary.encode(self._transaction_fee, type_='currency'))
        # encode refund coin output
        if self._refund_coin_output:
            buffer.extend([1])
            buffer.extend(binary.encode(self._refund_coin_output))
        else:
            buffer.extend([0])

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)

# _compute_monthly_bot_fees computes the total monthly fees required for the given months,
# using the given oneCoin value as the currency's unit value.
def _compute_monthly_bot_fees(months):
    multiplier = months * tfconst.BOT_MONTHLY_FEE_MULTIPLIER
    fees = HASTINGS_TFT_VALUE * multiplier
    if months < 12:
        return fees
    if months < 24:
        return int(fees * 0.7)
    return int(fees * 0.5)

class TfchainPublicKeySignaturePair:
    """
    TfchainPublicKeySignaturePair class
    """
    def __init__(self, public_key, signature):
        self._public_key = public_key
        self._signature = signature
    
    @classmethod
    def from_dict(cls, pair_info):
        """
        Creates a new TfchainPublicKeySignaturePair from dict
        
        @param pair_info: JSON dict representing a TfchainPublicKeySignaturePair
        """
        if 'publickey' in pair_info and 'signature' in pair_info:
            return cls(
                public_key = tftsig.SiaPublicKey.from_string(pair_info['publickey']),
                signature = pair_info['signature'],
            )
    
    @property
    def public_key(self):
        return self._public_key
    @public_key.setter
    def public_key(self, key):
        self._public_key = key
    
    @property
    def signature(self):
        return self._signature
    @signature.setter
    def signature(self, sig):
        self.signature = sig

    @property
    def json(self):
        """
        Returns a json encoded version of the TfchainPublicKeySignaturePair
        """
        return {
            'publickey': self._public_key.json,
            'signature': self._signature
        }

def sign_bot_transaction(transaction, public_key, secret_key):
    """
    Sign the pair using the secret key and fulfillment
    """
    sig_ctx = {
        'input_idx': 0,
        'transaction': transaction,
        'secret_key': secret_key
    }
    fulfillment = SingleSignatureFulfillment(pub_key=public_key)
    fulfillment.sign(sig_ctx=sig_ctx)
    return fulfillment._signature.hex()

class CoinInput:
    """
    CoinIput class
    """
    def __init__(self, parent_id, fulfillment):
        """
        Initializes a new coin input object
        """
        self._parent_id = parent_id
        self._fulfillment = fulfillment


    @classmethod
    def from_dict(cls, ci_info):
        """
        Creates a new CoinInput from dict

        @param ci_info: JSON dict representing a coin input
        """
        if 'fulfillment' in ci_info:
            f = FulfillmentFactory.from_dict(ci_info['fulfillment'])
            if 'parentid' in ci_info:
                return cls(parent_id=ci_info['parentid'],
                           fulfillment=f)

    @property
    def parent_id(self):
        return self._parent_id


    @property
    def json(self):
        """
        Returns a json encoded version of the Coininput
        """
        return {
            'parentid': self._parent_id,
            'fulfillment': self._fulfillment.json
        }


    def sign(self, input_idx, transaction, secret_key):
        """
        Sign the input using the secret key
        """
        sig_ctx = {
            'input_idx': input_idx,
            'transaction': transaction,
            'secret_key': secret_key
        }
        self._fulfillment.sign(sig_ctx=sig_ctx)


class CoinOutput:
    """
    CoinOutput calss
    """
    def __init__(self, value, condition):
        """
        Initializes a new coinoutput
        """
        self._value = value
        self._condition = condition


    @classmethod
    def from_dict(cls, co_info):
        """
        Creates a new CoinOutput from dict

        @param co_info: JSON dict representing a coin output
        """
        if 'condition' in co_info:
            condition = UnlockCondtionFactory.from_dict(co_info['condition'])
            if 'value' in co_info:
                return cls(value=int(co_info['value']),
                           condition=condition)


    @property
    def binary(self):
        """
        Returns a binary encoded version of the CoinOutput
        """
        result = bytearray()
        result.extend(binary.encode(self._value, type_='currency'))
        result.extend(binary.encode(self._condition))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the CointOutput
        """
        return {
            'value': str(self._value),
            'condition': self._condition.json
        }
