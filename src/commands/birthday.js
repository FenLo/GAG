const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { setBirthday } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('birthday')
        .setDescription('Bir kullanıcının doğum gününü ayarlar.')
        .addUserOption(option =>
            option.setName('user')
                .setDescription('Kullanıcı')
                .setRequired(true))
        .addIntegerOption(option =>
            option.setName('month')
                .setDescription('Ay (1-12)')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(12))
        .addIntegerOption(option =>
            option.setName('day')
                .setDescription('Gün (1-31)')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(31))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const user = interaction.options.getUser('user');
        const month = interaction.options.getInteger('month');
        const day = interaction.options.getInteger('day');

        setBirthday(user.id, user.tag, interaction.guild.id, month, day);

        await interaction.reply({
            content: `🎂 ${user} kullanıcısının doğum günü ${day}/${month} olarak ayarlandı!`,
            ephemeral: true
        });
    }
};
