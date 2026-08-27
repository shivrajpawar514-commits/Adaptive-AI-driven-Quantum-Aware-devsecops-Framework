const User = require('../models/user.model');

class UserRepository {
  async create(userData) {
    const user = new User(userData);
    return user.save();
  }

  async findByEmail(email) {
    return User.findOne({ email });
  }

  async findByUsername(username) {
    return User.findOne({ username });
  }

  async findById(id) {
    return User.findById(id).select('-password');
  }
}

module.exports = new UserRepository();
